import logging

from .base import ComponentFile


logger = logging.getLogger(__name__)


# TODO: figure out most basic permissions
lambda_base = '''description: '{description}'
iamRoleStatements: []
python_requirements: []
environment: {{}}
'''.format

lambda_lambda = '''lambda:
  memorySize: 128
  timeout: 60
'''.format

lambda_batch = '''batch:
  Resources:
    {name}ComputeEnvironment:
      Type: AWS::Batch::ComputeEnvironment
      Properties:
        Type: MANAGED
        ServiceRole:
          Fn::GetAtt: [ BatchServiceRole, Arn ]
        ComputeResources:
          MaxvCpus: ${{self:custom.batch.BasicComputeEnvironments.MaxvCpus}}
          SecurityGroupIds: ${{self:custom.batch.SecurityGroupIds}}
          Subnets: ${{self:custom.batch.Subnets}}
          InstanceTypes:
            - optimal
          Type: SPOT
          AllocationStrategy: BEST_FIT_PROGRESSIVE
          SpotIamFleetRole:
            Fn::GetAtt: [ EC2SpotRole, Arn ]
          MinvCpus: 0
          InstanceRole:
            Fn::GetAtt: [ BatchInstanceProfile, Arn ]
          Tags: {{"Name": "Batch Instance - #{{AWS::StackName}}"}}
          DesiredvCpus: 0
        State: ENABLED
    {name}JobQueue:
      Type: AWS::Batch::JobQueue
      Properties:
        ComputeEnvironmentOrder:
          - Order: 1
            ComputeEnvironment: !Ref {name}ComputeEnvironment
        State: ENABLED
        Priority: 1
    {name}AsBatchJob:
      Type: "AWS::Batch::JobDefinition"
      Properties:
        JobDefinitionName: '#{{AWS::StackName}}-{name}'
        Type: Container
        Parameters:
          lambda_function: ""
          url: ""
        ContainerProperties:
          Command:
            - run
            - Ref::lambda_function
            - Ref::url
          Environment: []
          Memory: 128
          Vcpus: 1
          Image: 'cirrusgeo/run-lambda:0.2.1'
        RetryStrategy:
          Attempts: 1
'''.format


default_workflow = '''name: ${{self:service}}-${{self:provider.stage}}-{name}
definition:
  Comment: {description}
  StartAt: publish
  States:
    publish:
      Type: Task
      Resource:
        Fn::GetAtt: [publish, Arn]
      End: True
      Retry:
        - ErrorEquals: ["Lambda.TooManyRequestsException", "Lambda.Unknown"]
          IntervalSeconds: 1
          BackoffRate: 2.0
          MaxAttempts: 5
      Catch:
        - ErrorEquals: ["States.ALL"]
          ResultPath: $.error
          Next: failure
    failure:
      Type: Fail
'''.format


class BaseDefinition(ComponentFile):
    def __init__(self, *args, name='definition.yml', **kwargs):
        super().__init__(*args, name=name, **kwargs)

    @staticmethod
    def content_fn(component) -> str:
        return ''


class LambdaDefinition(BaseDefinition):
    @staticmethod
    def content_fn(component) -> str:
        content = lambda_base(description=component.description)
        if getattr(component, 'lambda_enabled', True):
            content += '\n' + lambda_lambda()
        if getattr(component, 'batch_enabled', False):
            content += '\n' + lambda_batch(name=component.name)
        return content


class StepFunctionDefinition(BaseDefinition):
    @staticmethod
    def content_fn(component) -> str:
        return default_workflow(
            name=component.name,
            description=component.description,
        )
