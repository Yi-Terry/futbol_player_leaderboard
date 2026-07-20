resource "aws_glue_catalog_database" "player_leaderboard_db" {
    name = "player_leaderboard"
}

resource "aws_athena_workgroup" "pipeline_work_group" {
    name = "player-leaderboard-workgroup"
    configuration {
        enforce_workgroup_configuration = true
        publish_cloudwatch_metrics_enabled = true

        result_configuration {
            output_location = "s3://${var.bucket_name}/athena-results/"
        }
    }
}

output "glue_database_name" {
    value = aws_glue_catalog_database.player_leaderboard_db.name
}

output "athena_workgroup_name" {
    value = aws_athena_workgroup.pipeline_work_group.name
}