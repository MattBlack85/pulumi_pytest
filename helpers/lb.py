from pulumi import get_stack
from pulumi_aws import alb

from configuration.s3 import LOGGING_BUCKET_NAME


def setup_port_forwarding(
    product_name: str,
    load_balancer_arn: str,
    port: int = 80,
    protocol: str = 'HTTP',
    forward_port: int = 443,
    forward_protocol: str = 'HTTPS',
):
    """
    Common utility to setup quickly a forwarding rule, given a traffic port, a port to forwad traffic to
    and a protocol, it creates a rule that forwards traffic.

    Arguments:
        project_name -- The name of this product
        load_balancer_arn -- The ARN of the load balancer.
        port -- The port where traffic comes
        protocol -- if the traffic port accepts HTTP or HTTPS
        forward_to -- The port where to forward traffic
        forward_protocol -- if the forwarded port accepts HTTP or HTTPS
    """
    LISTENER_NAME = f'{product_name}-{port}-elb-{protocol}-listener'
    return alb.Listener(
        LISTENER_NAME,
        opts=None,
        default_actions=[
            {
                'redirect': {
                    'port': forward_port,
                    'protocol': forward_protocol,
                    'status_code': 'HTTP_301',
                },
                'type': 'redirect',
            }
        ],
        load_balancer_arn=load_balancer_arn,
        port=80,
        protocol=protocol,
    )


def setup_external_load_balancer(
    project_name: str,
    vpc_info: dict,
    security_groups: list,
    forward_http_to_https: bool = True,
):
    RESOURCE_NAME = f'{project_name}-ext-lb'

    load_balancer = alb.LoadBalancer(
        RESOURCE_NAME,
        access_logs=LOGGING_BUCKET_NAME.apply(
            lambda bucket: {
                'bucket': bucket,
                'enabled': True,
                'prefix': f'{project_name}/external',
            }
        ),
        internal=False,
        security_groups=security_groups,
        subnets=vpc_info.apply(
            lambda vpc_info: [subnet for subnet in vpc_info['public_subnets']]
        ),  # The ids of all the public subnets in vpc_info
        tags={'env': get_stack(), 'Name': RESOURCE_NAME, 'product': project_name},
    )

    if forward_http_to_https:
        setup_port_forwarding(
            project_name,
            load_balancer.arn,
        )

    return load_balancer


def setup_internal_load_balancer(project_name: str, vpc_info: dict, security_groups: list):

    RESOURCE_NAME = f'{project_name}-int-lb'

    load_balancer = alb.LoadBalancer(
        RESOURCE_NAME,
        access_logs=LOGGING_BUCKET_NAME.apply(
            lambda bucket: {
                'bucket': bucket,
                'enabled': True,
                'prefix': f'{project_name}/internal',
            }
        ),
        internal=True,
        security_groups=security_groups,
        subnets=vpc_info.apply(
            lambda vpc_info: [subnet for subnet in vpc_info['private_subnets']]
        ),  # The ids of all the private subnets in vpc_info
        tags={'env': get_stack(), 'Name': RESOURCE_NAME, 'product': project_name},
    )

    return load_balancer
