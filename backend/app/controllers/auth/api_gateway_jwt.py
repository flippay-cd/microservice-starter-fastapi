from exp_auth.jwt import JWTDecoder
from exp_auth.jwt.exceptions import JWTException
from fastapi import HTTPException, Request, status


class ApiGatewayJWTAuth:
    """
    Authentication using API Gateway JWT token.
    Returns user_id if the user was successfully authenticated.
    """

    auth_header = "Authorization"

    def __init__(self, decoder: JWTDecoder):
        self.decoder = decoder

    async def __call__(self, request: Request) -> dict:
        token = self._get_token_from_request(request)
        try:
            payload = self.decoder.process(token)
        except JWTException as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Ошибка JWT токена: {e}")

        if not payload.get("user_id"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Отсутствует валидный user_id")

        return payload

    def _get_token_from_request(self, request: Request) -> str:
        token_header = request.headers.get(self.auth_header, "")

        if not token_header:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Auth token не предоставлен")

        token_split = token_header.split()

        if not len(token_split) == 2 or not token_split[0] == "Bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ожидается Bearer-схема")

        return token_split[1]
