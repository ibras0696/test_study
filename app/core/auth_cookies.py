from fastapi import Response

from config import settings


# Имена cookies, в которых клиент будет хранить access и refresh токены.
ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    """
    Устанавливает auth cookies с access и refresh токенами.

    Access cookie доступна для всего сайта, а refresh cookie ограничена
    путём /auth, потому что refresh-токен нужен только auth-эндпоинтам.
    """

    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,  # cookie недоступна из JavaScript
        secure=settings.COOKIE_SECURE,  # отправлять только по HTTPS, если включено в config
        samesite=settings.COOKIE_SAMESITE,  # защита от части CSRF-сценариев
        path="/",  # access cookie отправляется на все пути приложения
    )

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/auth",  # refresh cookie отправляется только на /auth/*
    )


def clear_auth_cookies(response: Response) -> None:
    """
    Удаляет auth cookies с access и refresh токенами.

    path должен совпадать с тем, который использовался при установке cookie,
    иначе браузер может не удалить нужную cookie.
    """

    response.delete_cookie(
        key=ACCESS_COOKIE_NAME,
        path="/",
    )

    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/auth",
    )
