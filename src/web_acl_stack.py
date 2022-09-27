from aws_cdk import Aws, CfnOutput, Fn, Stack
from aws_cdk import aws_logs as logs
from aws_cdk import aws_wafv2 as waf
from constructs import Construct


class CustomWebAclStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)
        waf_rules = [
            # 1, AWS Bot Control rule group
            waf.CfnWebACL.RuleProperty(
                name="AWS-BotControl",
                priority=1,
                override_action=waf.CfnWebACL.OverrideActionProperty(none={}),
                statement=waf.CfnWebACL.StatementProperty(
                    managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                        name="AWSManagedRulesBotControlRuleSet", vendor_name="AWS"
                    )
                ),
                visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name=f"AWSManagedRulesBotControlRuleSetMetrics-{Aws.STACK_NAME}",
                    sampled_requests_enabled=True,
                ),
            ),
            # 2 Amazon IP reputation list managed rule group
            waf.CfnWebACL.RuleProperty(
                name="AWS-AmazonIpReputationList",
                priority=2,
                override_action=waf.CfnWebACL.OverrideActionProperty(none={}),
                statement=waf.CfnWebACL.StatementProperty(
                    managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                        name="AWSManagedRulesAmazonIpReputationList", vendor_name="AWS"
                    )
                ),
                visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name=f"AWSManagedRulesAmazonIpReputationListMetrics-{Aws.STACK_NAME}",
                    sampled_requests_enabled=True,
                ),
            ),
            # 3, Anonymous IP list managed rule group
            waf.CfnWebACL.RuleProperty(
                name="AWS-ManagedRulesAnonymousIpList",
                priority=3,
                override_action=waf.CfnWebACL.OverrideActionProperty(none={}),
                statement=waf.CfnWebACL.StatementProperty(
                    managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                        name="AWSManagedRulesAnonymousIpList", vendor_name="AWS"
                    )
                ),
                visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name=f"AWSManagedRulesAnonymousIpListMetrics-{Aws.STACK_NAME}",
                    sampled_requests_enabled=True,
                ),
            ),
            # 4, AWS general rules (Core rule set)
            waf.CfnWebACL.RuleProperty(
                name="AWS-ManagedRulesCommonRuleSet",
                priority=4,
                override_action=waf.CfnWebACL.OverrideActionProperty(none={}),
                statement=waf.CfnWebACL.StatementProperty(
                    managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                        name="AWSManagedRulesCommonRuleSet", vendor_name="AWS"
                    )
                ),
                visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name=f"AWSManagedRulesCommonRuleSetMetrics-{Aws.STACK_NAME}",
                    sampled_requests_enabled=True,
                ),
            ),
            # 5, AWS Known Bad inputs rules
            waf.CfnWebACL.RuleProperty(
                name="AWS-ManagedRulesKnownBadInputsRuleSet",
                priority=5,
                override_action=waf.CfnWebACL.OverrideActionProperty(none={}),
                statement=waf.CfnWebACL.StatementProperty(
                    managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                        name="AWSManagedRulesKnownBadInputsRuleSet",
                        vendor_name="AWS",
                    )
                ),
                visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name=f"AWSManagedRulesKnownBadInputsRuleSetMetrics-{Aws.STACK_NAME}",
                    sampled_requests_enabled=True,
                ),
            ),
            # 6, Admin protection managed rule group
            waf.CfnWebACL.RuleProperty(
                name="AWS-AdminProtection",
                priority=6,
                override_action=waf.CfnWebACL.OverrideActionProperty(none={}),
                statement=waf.CfnWebACL.StatementProperty(
                    managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                        name="AWSManagedRulesAdminProtectionRuleSet", vendor_name="AWS"
                    )
                ),
                visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name=f"AWSManagedRulesAdminProtectionRuleSetMetrics-{Aws.STACK_NAME}",
                    sampled_requests_enabled=True,
                ),
            ),
        ]

        # Define Web Application Firewall ACL
        web_acl = waf.CfnWebACL(
            self,
            "rWebACL",
            default_action=waf.CfnWebACL.DefaultActionProperty(allow={}),
            scope="CLOUDFRONT",
            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                sampled_requests_enabled=True,
                metric_name=f"WebAclMetrics-{Aws.STACK_NAME}",
            ),
            rules=waf_rules,
        )

        # Web ACL log group
        web_acl_lg = logs.LogGroup(
            self,
            "rAmplifWebAclLogGroup",
            retention=logs.RetentionDays.SIX_MONTHS,
            log_group_name=f"aws-waf-logs-{Aws.STACK_NAME}",
        )

        waf.CfnLoggingConfiguration(
            self,
            "rAmplifWebAclLoggingConfig",
            log_destination_configs=[
                Fn.select(0, Fn.split(":*", web_acl_lg.log_group_arn))
            ],
            resource_arn=web_acl.attr_arn,
        )

        self.custom_web_acl = web_acl

        CfnOutput(self, "oWebAclId", value=web_acl.attr_arn)
