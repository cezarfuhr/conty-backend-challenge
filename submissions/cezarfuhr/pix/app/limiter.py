from slowapi import Limiter
from slowapi.util import get_remote_address

# O limiter usara o endereco de IP do cliente como chave
limiter = Limiter(key_func=get_remote_address)
