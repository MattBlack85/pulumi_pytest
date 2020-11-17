import pulumi
import pytest

TEST_PROJECT_NAME = 'pulumi-testy'

s3_stack_state = {
    'certs_bucket_name': 'test-electric-fence',
    'lambda_bucket_id': 'test-foo-lambdas',
    'logging_bucket_name': 'test-foo-elb-logs',
    'prometheus_bucket_name': 'test-prometheus',
}


class PulumiMock(pulumi.runtime.Mocks):
    def new_resource(self, type_, name, inputs, provider, id_):

        if type_ == 'pulumi:pulumi:StackReference':
            return [name, {**inputs, **s3_stack_state}]

        return [name, inputs]

    def call(self, token, args, provider):
        return {}


@pytest.fixture(autouse=True)
def config_init(scope='function'):
    pulumi.runtime.set_config('aws:region', 'us-east-1')
    pulumi.runtime.set_mocks(
        PulumiMock(), project=TEST_PROJECT_NAME, stack=f'{TEST_PROJECT_NAME}-stack'
    )
