from pulumi import StackReference, get_stack

S3_STACK_REFERENCE = StackReference(f's3/{get_stack()}')

CERTS_BUCKET_NAME = S3_STACK_REFERENCE.get_output('certs_bucket_name')
LOGGING_BUCKET_NAME = S3_STACK_REFERENCE.get_output('logging_bucket_name')
PROMETHEUS_BUCKET_NAME = S3_STACK_REFERENCE.get_output('prometheus_bucket_name')
