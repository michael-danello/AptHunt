from fp.fp import FreeProxy

def get_new_proxy_server():
    return FreeProxy(rand=True, country_id='US').get()