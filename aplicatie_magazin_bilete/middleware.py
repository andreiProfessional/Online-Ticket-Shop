from aplicatie_magazin_bilete.models import Accesare


class MiddlewareLogAccesari:
    accesari = []

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        accesare = Accesare(request.META.get('REMOTE_ADDR'), request.get_full_path())
        MiddlewareLogAccesari.accesari.append(accesare)
        return self.get_response(request)
