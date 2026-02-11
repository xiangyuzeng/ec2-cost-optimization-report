# GuardDuty EKS Protection Investigation Report

**Date**: 2026-02-11
**AWS Account**: 257394478466
**IAM User**: databasecheck

## Executive Summary

Investigation to check Amazon GuardDuty EKS Runtime Monitoring status was **unable to complete** due to IAM permission restrictions.

## Environment Discovery

### AWS Account
```json
{
    "UserId": "AIDATX3PIBWBHOR7ZX46M",
    "Account": "257394478466",
    "Arn": "arn:aws:iam::257394478466:user/databasecheck"
}
```

### EKS Clusters Found (us-east-1)
```json
{
    "clusters": [
        "prod-native-eks-us",
        "prod-worker01-eks-us"
    ]
}
```

## Permission Issues Encountered

### 1. GuardDuty Access - DENIED
```
An error occurred (AccessDeniedException) when calling the ListDetectors operation:
User: arn:aws:iam::257394478466:user/databasecheck is not authorized to perform:
guardduty:ListDetectors on resource: arn:aws:guardduty:us-east-1:257394478466:detector/*
because no identity-based policy allows the guardduty:ListDetectors action
```

### 2. EKS Kubernetes API Access - UNAUTHORIZED
```
Unauthorized (401) when attempting to access:
- prod-native-eks-us
- prod-worker01-eks-us
```

The `databasecheck` user is not configured in the EKS cluster's aws-auth ConfigMap or RBAC.

## Required Permissions

To complete this investigation, the following permissions are needed:

### For GuardDuty Status Check
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "guardduty:ListDetectors",
                "guardduty:GetDetector"
            ],
            "Resource": "*"
        }
    ]
}
```

### For EKS Namespace Check
1. Add IAM user/role to EKS cluster's `aws-auth` ConfigMap
2. Create RBAC ClusterRole with namespace list permissions:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: namespace-reader
rules:
- apiGroups: [""]
  resources: ["namespaces", "pods", "daemonsets"]
  verbs: ["get", "list"]
```

## Commands to Run (With Proper Permissions)

```bash
# 1. Check if amazon-guardduty namespace exists
kubectl get namespace amazon-guardduty -o json | jq '{
  name: .metadata.name,
  labels: .metadata.labels,
  annotations: .metadata.annotations,
  created: .metadata.creationTimestamp
}'

# 2. Check resources in the namespace
kubectl get all -n amazon-guardduty

# 3. Check DaemonSet (GuardDuty agent)
kubectl get daemonset -n amazon-guardduty -o wide

# 4. Check namespace labels (identifies AWS-managed resources)
kubectl get namespace amazon-guardduty -o jsonpath='{.metadata.labels}' | jq .

# 5. Check GuardDuty EKS protection status
aws guardduty list-detectors --region us-east-1
aws guardduty get-detector --detector-id <detector-id> --region us-east-1 | \
  jq '.features[] | select(.name == "EKS_RUNTIME_MONITORING" or .name == "RUNTIME_MONITORING")'
```

## Expected GuardDuty EKS Protection Configuration

When GuardDuty EKS Runtime Monitoring is enabled, you should see:

1. **Namespace**: `amazon-guardduty`
2. **DaemonSet**: `aws-guardduty-agent` running on all nodes
3. **Labels**: `app.kubernetes.io/managed-by: aws.amazon.com/eks`
4. **GuardDuty Feature Status**:
```json
{
  "name": "EKS_RUNTIME_MONITORING",
  "status": "ENABLED"
}
```

## Next Steps

1. Request IAM policy updates for `guardduty:ListDetectors` and `guardduty:GetDetector`
2. Add the `databasecheck` user to EKS cluster RBAC (or use a role with existing access)
3. Re-run the investigation commands
4. Document GuardDuty EKS protection status for both clusters

## References

- [Amazon GuardDuty EKS Runtime Monitoring](https://docs.aws.amazon.com/guardduty/latest/ug/eks-runtime-monitoring.html)
- [EKS Cluster Authentication](https://docs.aws.amazon.com/eks/latest/userguide/cluster-auth.html)
