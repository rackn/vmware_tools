import os
import vcr


def fixture_path(local_path=None):
    this_file = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_file, local_path)


my_vcr = vcr.VCR(
    serializer='json',
    record_mode='once',
    cassette_library_dir=fixture_path('../fixtures/api')
)
