# Authentication
* User authentication is added using API Gateway
* The service must be accessible from the outside - traffic to it must go through ingress.
* In staging and production helm `values.yaml` in the `ingress` block, add the `gateway_auth_enabled` variable and set the value to `true`.
* Now all traffic to the service will go through the api gateway. A client request without a valid auth cookie or header will not reach the microservice.
* Add the `securitySchemes` component and the scheme for the JWT token to the openapi scheme.
* Add this scheme for the endpoint that requires authentication. Example in the template - `POST /v1/article`
* Next, you will need to add receiving a public key for signature verification and a token handler that will transfer data to the controller. Example of these dependencies in container: `jwt_public_key`, `jwt_decoder`, `process_auth_token_bearer`
