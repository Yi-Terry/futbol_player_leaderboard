terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "~> 5.0"
    }
  }
}

provider "aws" {
    region = var.aws_region
}

variable "aws_region" {
    default = "us-east-2"
}

variable "bucket_name" {
    description = "unqiue name for s3 bucket"
    type = string
    default = "player-leaderboard-pipeline-terry"
}

resource "aws_iam_user" "pipeline_user" {
    name = "player-leaderboard-pipeline"
}

resource "aws_iam_policy" "pipeline_policy" {
    name = "PlayerLeaderboardPipelinePolicy"
    description = "Scoped access for the player leaderboard pipeline (s3 + Glue + Athena)"

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Sid = "S3ProjectBucketAccess"
                Effect = "Allow"
                Action = [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ]
                Resource = [
                    "arn:aws:s3:::${var.bucket_name}",
                    "arn:aws:s3:::${var.bucket_name}/*"
                ]
            },
            {
                Sid = "GlueCatalogAccess"
                Effect = "Allow"
                Action = [
                     "glue:GetDatabase",
                    "glue:CreateDatabase",
                    "glue:GetTable",
                    "glue:GetTables",
                    "glue:CreateTable",
                    "glue:UpdateTable",
                    "glue:GetPartitions",
                    "glue:BatchCreatePartition",
                    "glue:StartCrawler",
                    "glue:GetCrawler",
                    "glue:CreateCrawler"
                ]
                Resource = "*"
            },
            {
                Sid = "AthenaQueryAccess"
                Effect = "Allow"
                Action = [
                    "athena:StartQueryExecution",
                    "athena:GetQueryExecution",
                    "athena:GetQueryResults",
                    "athena:StopQueryExecution",
                    "athena:GetWorkGroup"
                ]
                Resource = "*"
            },
        ]
    })
}

resource "aws_iam_user_policy_attachment" "attach" {
    user = aws_iam_user.pipeline_user.name
    policy_arn = aws_iam_policy.pipeline_policy.arn
}

resource "aws_iam_access_key" "pipeline_key" {
    user = aws_iam_user.pipeline_user.name
}

output "access_key_id" {
    value = aws_iam_access_key.pipeline_key.id
}

output "secret_access_key" {
    value = aws_iam_access_key.pipeline_key.secret
    sensitive = true
}