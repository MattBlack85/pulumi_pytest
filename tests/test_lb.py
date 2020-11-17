import pulumi

from .factories import OutputFactory


@pulumi.runtime.test
def test_setup_external_load_balancer():
    from helpers.lb import setup_external_load_balancer

    test_project_name = 'test-external-lb'
    test_bucket = {
        'bucket': 'test-foo-elb-logs',
        'enabled': True,
        'prefix': f'{test_project_name}/external',
    }
    test_subnets = [
        'subnet-0',
        'subnet-1',
        'subnet-2',
    ]
    vpc_info = OutputFactory({'public_subnets': test_subnets})
    security_groups = []

    lb = setup_external_load_balancer(
        project_name=test_project_name, vpc_info=vpc_info, security_groups=security_groups
    )

    assert lb is not None

    def check_lb(args):
        id_, tags, internal, subnets, access_logs = args

        assert id_ == f'{test_project_name}-ext-lb'

        assert 'env' in tags
        assert 'Name' in tags
        assert 'product' in tags
        assert tags['env'] == pulumi.get_stack()
        assert tags['Name'] == f'{test_project_name}-ext-lb'
        assert tags['product'] == test_project_name

        assert internal is False

        assert subnets == test_subnets

        assert access_logs == test_bucket

    return pulumi.Output.all(lb.id, lb.tags, lb.internal, lb.subnets, lb.access_logs).apply(
        check_lb
    )


@pulumi.runtime.test
def test_setup_internal_load_balancer(create_alias_mock):
    from helpers.lb import setup_internal_load_balancer

    test_project_name = 'test-project-name'
    test_bucket = {
        'bucket': 'test-foo-elb-logs',
        'enabled': True,
        'prefix': f'{test_project_name}/internal',
    }
    test_subnets = [
        'subnet-0',
        'subnet-1',
        'subnet-2',
    ]
    vpc_info = OutputFactory({'private_subnets': test_subnets})
    security_groups = []

    lb = setup_internal_load_balancer(
        project_name=test_project_name, vpc_info=vpc_info, security_groups=security_groups
    )

    assert lb is not None
    create_alias_mock.assert_called_once()

    def check_lb(args):
        id_, tags, internal, subnets, access_logs = args

        assert id_ == f'{test_project_name}-int-lb'

        assert 'env' in tags
        assert 'Name' in tags
        assert 'product' in tags
        assert tags['env'] == pulumi.get_stack()
        assert tags['Name'] == f'{test_project_name}-int-lb'
        assert tags['product'] == test_project_name

        assert internal is True

        assert subnets == test_subnets

        assert access_logs == test_bucket

    return pulumi.Output.all(lb.id, lb.tags, lb.internal, lb.subnets, lb.access_logs).apply(
        check_lb
    )


@pulumi.runtime.test
def test_setup_port_forwarding():
    from helpers.lb import setup_port_forwarding

    test_project_name = 'test-project-name'

    listener = setup_port_forwarding(test_project_name, load_balancer_arn='test:arn')

    assert listener is not None

    def check_listener(args):
        port, protocol, default_actions = args

        expected_default_actions = [
            {
                'redirect': {'port': 443, 'protocol': 'HTTPS', 'status_code': 'HTTP_301'},
                'type': 'redirect',
            }
        ]

        assert port == 80
        assert protocol == 'HTTP'
        assert default_actions == expected_default_actions

    return pulumi.Output.all(
        listener.port,
        listener.protocol,
        listener.default_actions,
    ).apply(check_listener)
