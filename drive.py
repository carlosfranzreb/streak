import google.oauth2.credentials
import google_auth_oauthlib.flow

flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'credentials.json',
    scope=['https://www.googleapis.com/auth/drive'])

flow.redirect_uri = 'https://www.example.com/oauth2callback'

authorization_url, state = flow.authorization_url(
    access_type='offline', include_granted_scopes='true')
