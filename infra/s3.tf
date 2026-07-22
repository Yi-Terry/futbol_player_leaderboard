resource "aws_s3_bucket" "pipeline_bucket" {
    bucket = var.bucket_name
}

resource "aws_s3_bucket_public_access_block" "pipeline_bucket_block" { 
    bucket = aws_s3_bucket.pipeline_bucket.id

    block_public_acls = true
    block_public_policy = true
    ignore_public_acls = true
    restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "pipeline_bucket_versioning" {
    bucket = aws_s3_bucket.pipeline_bucket.id
    versioning_configuration {
      status = "Enabled"
    }
}

resource "aws_s3_object" "raw_prefix" {
    bucket = aws_s3_bucket.pipeline_bucket.id
    key = "raw/"
}


resource "aws_s3_object" "processed_prefix" {
    bucket = aws_s3_bucket.pipeline_bucket.id
    key = "processed/"
}


resource "aws_s3_object" "athena_results_prefix" {
    bucket = aws_s3_bucket.pipeline_bucket.id
    key = "athena-results/"
}

output "bucket_name" {
    value = aws_s3_bucket.pipeline_bucket.bucket
}