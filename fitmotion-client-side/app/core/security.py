from fastapi.openapi.models import SecurityScheme, OAuthFlows, OAuthFlowImplicit
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.core.config.settings import settings

firebase_oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://accounts.google.com/o/oauth2/auth",
    tokenUrl=f"https://oauth2.googleapis.com/token",
    scopes={
        "openid": "OpenID Connect",
        "email": "Email address",
        "profile": "Profile information"
    }
)

swagger_firebase_auth = SecurityScheme(
    type="oauth2",
    flows=OAuthFlows(
        implicit=OAuthFlowImplicit(
            authorizationUrl=f"https://{settings.FIREBASE_AUTH_DOMAIN}/__/auth/handler",
            scopes={
                "openid": "OpenID Connect",
                "email": "Email address",
                "profile": "Profile information"
            }
        )
    )
)