# This is a throw-away script for the purpose of tracking down a bug
# in notion-py. 
# The script creates a subclass on NotionClient called NotionClientWithLogger
# that basically just added a stdout streaming logger to NotionClient requests.
import logging
import sys  
import textwrap  
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from notion.client import NotionClient
    
root = logging.getLogger('httplogger')


def logRoundtrip(response, *args, **kwargs):
    extra = {'req': response.request, 'res': response}
    root.debug('HTTP roundtrip', extra=extra)
    

class HttpFormatter(logging.Formatter):

    def _formatHeaders(self, d):
        return '\n'.join(f'{k}: {v}' for k, v in d.items())

    def formatMessage(self, record):
        result = super().formatMessage(record)
        if record.name == 'httplogger':
            result += textwrap.dedent('''
                ---------------- request ----------------
                {req.method} {req.url}
                {reqhdrs}

                {req.body}
                ---------------- response ----------------
                {res.status_code} {res.reason} {res.url}
                {reshdrs}

                {res.text}
            ''').format(
                req=record.req,
                res=record.res,
                reqhdrs=self._formatHeaders(record.req.headers),
                reshdrs=self._formatHeaders(record.res.headers),
            )

        return result

formatter = HttpFormatter('{asctime} {levelname} {name} {message}', style='{')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
root.addHandler(handler)
root.setLevel(logging.DEBUG)

def create_session(client_specified_retry=None):
    """
    retry on 502
    """
    session = Session()
    session.hooks['response'].append(logRoundtrip)
    if client_specified_retry:
        retry = client_specified_retry
    else:
        retry = Retry(
            5,
            backoff_factor=0.3,
            status_forcelist=(502, 503, 504),
            # CAUTION: adding 'POST' to this list which is not technically idempotent
            method_whitelist=(
                "POST",
                "HEAD",
                "TRACE",
                "GET",
                "PUT",
                "OPTIONS",
                "DELETE",
            ),
        )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

class NotionClientWithLogger(NotionClient):
    def __init__(
        self,
        token_v2=None,
        monitor=False,
        start_monitoring=False,
        enable_caching=False,
        cache_key=None,
        email=None,
        password=None,
        client_specified_retry=None,
    ):
        super(NotionClientWithLogger, self).__init__(
            token_v2=token_v2,
            monitor=monitor,
            start_monitoring=start_monitoring,
            enable_caching=enable_caching,
            cache_key=cache_key,
            email=email,
            password=password,
            client_specified_retry=client_specified_retry,
        )
        self.session = create_session(client_specified_retry)