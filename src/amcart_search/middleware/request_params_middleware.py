import logging
import time
import uuid
import json
import re
from django.urls import resolve
from django.conf import settings
from json.decoder import JSONDecodeError

from api.tasks import store_request_logging

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()
logger = logging.getLogger(__name__)


def get_current_request_id():
    """ returns the request id for this thread """
    return getattr(_thread_locals, "request_id", None)


class RequestParameterMiddleware(object):
    """
    middleware for setting parameters in request response cycle
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        """Handle new-style middleware here."""
        response = self.process_request(request)
        if response is None:
            # If process_request returned None, we must call the next middleware or
            # the view. Note that here, we are sure that self.get_response is not
            # None because this method is executed only in new-style middlewares.
            response = self.get_response(request)

        response = self.process_response(request, response)
        return response

    def process_request(self, request):
        """
        Setting content type in request for getting different response type from views.
        :param request:
        :return:
        """
        data = request.GET.dict()
        content_type = data.get('content_type')
        request.content_type = content_type
        request_id = uuid.uuid4().hex[:10]
        _thread_locals.request_id = request_id

        request.start_time = time.time()
        request._initial_http_body = getattr(request, '_body', request.body)
        url = resolve(request.path_info).url_name
        if request.method == "POST" and url in ["order-list","order-create"]:
            request._body = self.clean_json(request.body.decode('utf-8'))
        request.request_id = request_id


    def process_response(self, request, response):
        """
        Log the api stats data.
        :param request:
        :param response:
        :return:
        """
        if not hasattr(request, '_initial_http_body'):
            return response

        response_time = time.time() - request.start_time
        response_time = round(response_time, 5)

        if hasattr(request, 'user') and hasattr(request.user, 'email'):
            user_email = request.user.email
        else:
            user_email = ''
        request_payload = {
            'remote_address': self.get_client_ip(request),
            'request_method': request.method,
            'request_path': request.get_full_path(),
        }
        response_payload = {
            'response_status': response.status_code,
            'user_email': user_email,
            'response_time': response_time,
            'request_auth_token': str(request.META.get('HTTP_AUTHORIZATION', ''))
        }
        time_message = self.custom_time_category(response_time)
        if response.status_code >=400 and settings.STORE_REQUEST_LOGGING and (request.method == "POST" or request.method == "DELETE"):
            request_payload['payload'] = str(self.get_request_payload(request))
            response_payload['response'] = str(self.get_response_payload(response))
            store_request_logging.apply_async(
                kwargs={
                    "time_slot_category":time_message,
                    "request_id":request.request_id,
                    "response_payload":response_payload,
                    "request_payload":request_payload
                },
                queue='default',
                routing_key='default.#'
            )
        logger.info(
            "{request_id} : request_params_middleware.py : MIDDLEWARE ::  Request Payload {request_payload} Response  Payload {message} Process Time range :: {time_message} ".format(
                request_id=request.request_id,
                message=str(response_payload),
                request_payload=str(request_payload),
                time_message=str(time_message)
            ))
        return response

    def get_request_payload(self, request_obj):
        payload = {}
        try:
            if request_obj.method == "POST":
                payload = request_obj.POST
                if not payload:
                    payload = request_obj.body
            elif request_obj.method == "GET":
                payload = request_obj.GET
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")
        except Exception as e:
            logger.info(
                "Request middleware:- Something went wrong in case of prepare payload and exception is :{}".format(
                    str(e)))
        return payload

    def get_response_payload(self, response):
        payload = {}
        try:
            try:
                payload = response.data
            except Exception as e:
                pass
            if not payload:
                payload = response.content
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")
        except Exception as e:
            logger.info(
                "Request middleware:- Something went wrong in case of prepare response payload and exception is :{}".format(
                    str(e)))
        return payload

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def custom_time_category(self, response_time):
        time_message = ''
        if 0 < response_time <= 10:
            time_message = '10ms'
        elif 11 < response_time <= 20:
            time_message = '20ms'
        elif 21 < response_time <= 50:
            time_message = '50ms'
        elif 51 < response_time <= 100:
            time_message = '100 ms'
        elif 101 < response_time <= 200:
            time_message = '200 ms'
        elif 201 < response_time <= 500:
            time_message = '500 ms'
        elif 501 < response_time <= 1000:
            time_message = '1000 ms'
        elif 1001 < response_time:
            time_message = '1000+ ms'
        return time_message

    def clean_json(self, info_row):
        try:
            json.loads(info_row)
            info = info_row.encode('utf-8')
        except JSONDecodeError:
            logger.info(f"we got a invalid json and now We are trying to fix that {info_row}")
            data = {}
            try:
                info_row = [ele for ele in re.split(r'"(\s*),(\s*)"', info_row) if ele.strip()]
                for s in info_row:
                    if not s and s.strip():
                        continue
                    key, val = s.split(":", maxsplit=1)
                    key = re.sub('\s+','',key)
                    key = key.strip().lstrip("{").strip('"')
                    val = re.sub('(\s*)"', '', val.lstrip('"').strip('\"}'))
                    data[key] = val
            except ValueError:
                logger.info(f"ERROR: {info_row}")
            info = json.dumps(data).encode('utf-8')
        except Exception as error:
            logger.info(f"json clean error {error} and {info_row}")
            info = info_row
        return info

