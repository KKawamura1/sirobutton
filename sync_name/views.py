from django.shortcuts import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.views import generic
from urllib.parse import parse_qsl

from typing import Any, Dict
from sync_name.settings import TWITTER_API_KEY, TWITTER_API_SECRET
from requests_oauthlib import OAuth1Session
import json
from .models import TwitterAccount


class GetOAuthView(generic.TemplateView):
    template_name = 'get_oauth.html'


class APIGetOAuthView(generic.View):

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        redirection_url = APIGetOAuthView._get_redirection_url(request)
        url = APIGetOAuthView._get_twitter_oauth_url(redirection_url)
        return HttpResponseRedirect(url)

    @classmethod
    def _get_twitter_oauth_url(cls, redirection_url: str) -> str:
        # See: https://qiita.com/mikan3rd/items/686e4978f9e1111628e9
        twitter = OAuth1Session(TWITTER_API_KEY, TWITTER_API_SECRET)
        response = twitter.post(
            'https://api.twitter.com/oauth/request_token',
            params={'oauth_callback': redirection_url}
        )
        request_token = dict(parse_qsl(response.content.decode('utf-8')))
        authenticate_endpoint = (f'https://api.twitter.com/oauth/authenticate'
                                 f'?oauth_token={request_token["oauth_token"]}')
        return authenticate_endpoint

    @classmethod
    def _get_redirection_url(cls, request: HttpRequest) -> str:
        return f'https://{request.get_host()}{reverse("sync_name:after_oauth")}'


class AfterOAuthView(generic.View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        oauth_token = request.GET.get('oauth_token')
        oauth_verifier = request.GET.get('oauth_verifier')

        twitter = OAuth1Session(
            TWITTER_API_KEY, TWITTER_API_SECRET, oauth_token, oauth_verifier
        )
        response = twitter.post(
            'https://api.twitter.com/oauth/access_token',
            params={'oauth_verifier': oauth_verifier}
        )
        access_token = dict(parse_qsl(response.content.decode("utf-8")))

        twitter_id = access_token['user_id']
        twitter_with_access = OAuth1Session(
            TWITTER_API_KEY, TWITTER_API_SECRET,
            access_token['oauth_token'], access_token['oauth_token_secret']
        )
        # Get now name
        response = twitter_with_access.get(
            'https://api.twitter.com/1.1/users/show.json',
            params={'user_id': twitter_id}
        )
        name: str = json.loads(response.text)['name']
        # Get object
        obj: TwitterAccount
        obj, _ = TwitterAccount.objects.get_or_create(
            twitter_id=str(twitter_id),
            defaults={
                'oauth_token': access_token['oauth_token'],
                'oauth_secret': access_token['oauth_token_secret'],
                'last_prefix': name
            }
        )
        # Compute new prefix
        if name.startswith(obj.last_prefix):
            new_prefix = obj.last_prefix
        else:
            new_prefix = name
        obj.last_prefix = new_prefix
        obj.save()
        # Compute new name
        response = twitter_with_access.get(
            'https://api.twitter.com/1.1/users/show.json',
            params={'screen_name': 'SIROyoutuber'},
        )
        siro_name: str = json.loads(response.text)['name']
        siro_prefix = '電脳少女シロ'
        if siro_name.startswith(siro_prefix):
            postfix = siro_name[len(siro_prefix):]
            new_name = new_prefix + postfix
        else:
            new_name = new_prefix
        # Update twitter name
        response = twitter_with_access.post(
            'https://api.twitter.com/1.1/account/update_profile.json',
            params={'name': new_name}
        )
        return HttpResponseRedirect(
            f'https://{request.get_host()}{reverse("sync_name:settings", kwargs={"pk": obj.id})}'
        )


class Settings(generic.DetailView):
    model = TwitterAccount
    context_object_name = 'account'
    template_name = 'setting_page.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        account: TwitterAccount = context['account']
        return context


class UpdateAllAPI(generic.View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # Check Siro-chan
        siro_prefix = '電脳少女シロ'
        siro_name: str = None
        # For each accounts
        account: TwitterAccount
        for account in TwitterAccount.objects.all():
            try:
                twitter_id = account.twitter_id
                twitter_with_access = OAuth1Session(
                    TWITTER_API_KEY, TWITTER_API_SECRET,
                    account.oauth_token, account.oauth_secret
                )
                # Get now name
                response = twitter_with_access.get(
                    'https://api.twitter.com/1.1/users/show.json',
                    params={'user_id': twitter_id}
                )
                name: str = json.loads(response.text)['name']
                # Compute new prefix
                if name.startswith(account.last_prefix):
                    new_prefix = account.last_prefix
                else:
                    new_prefix = name
                account.last_prefix = new_prefix
                account.save()
                # Check Siro-chan's name with cache
                if siro_name is None:
                    response = twitter_with_access.get(
                        'https://api.twitter.com/1.1/users/show.json',
                        params={'screen_name': 'SIROyoutuber'},
                    )
                    siro_name: str = json.loads(response.text)['name']
                # Compute new name
                if siro_name.startswith(siro_prefix):
                    postfix = siro_name[len(siro_prefix):]
                    new_name = new_prefix + postfix
                else:
                    new_name = new_prefix
                # Update twitter name
                response = twitter_with_access.post(
                    'https://api.twitter.com/1.1/account/update_profile.json',
                    params={'name': new_name}
                )
            except Exception:
                pass
        return JsonResponse(dict(status_code=0))

