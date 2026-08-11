# El Connector Profile se crea fuera de este módulo para no guardar credenciales
# SAP en el código. En producción debe utilizar HTTPS y conectividad privada.
resource "aws_appflow_flow" "sap_copa_to_landing" {
  count = var.create_appflow ? 1 : 0

  name        = "${local.name_prefix}-sap-copa"
  description = "Carga incremental SAP ECC/SLT ODP OData hacia S3 Landing"

  source_flow_config {
    connector_type         = "SAPOData"
    connector_profile_name = var.appflow_connector_profile_name

    source_connector_properties {
      sapo_data {
        object_path = var.appflow_sap_object_path
        pagination_config { max_page_size = 3000 }
        parallelism_config { max_page_size = 4 }
      }
    }
  }

  destination_flow_config {
    connector_type = "S3"

    destination_connector_properties {
      s3 {
        bucket_name   = aws_s3_bucket.landing.bucket
        bucket_prefix = "copa/appflow"

        s3_output_format_config {
          file_type                   = "PARQUET"
          preserve_source_data_typing = true
          aggregation_config { aggregation_type = "None" }
          prefix_config {
            prefix_type      = "PATH"
            prefix_format    = "YEAR_MONTH_DAY"
            prefix_hierarchy = ["EXECUTION_ID"]
          }
        }
      }
    }
  }

  trigger_config {
    trigger_type = "Scheduled"
    trigger_properties {
      scheduled {
        schedule_expression = var.appflow_schedule_expression
        data_pull_mode      = "Incremental"
        timezone            = "America/Argentina/Buenos_Aires"
      }
    }
  }

  task {
    task_type     = "Map_all"
    source_fields = []
    connector_operator { sapo_data = "NO_OP" }
  }

  lifecycle {
    precondition {
      condition     = var.appflow_connector_profile_name != null
      error_message = "Cuando create_appflow=true se debe indicar appflow_connector_profile_name."
    }

    precondition {
      condition     = var.appflow_sap_object_path != "REPLACE_WITH_COPA_ENTITY_SET"
      error_message = "Cuando create_appflow=true se debe indicar el EntitySet OData real de CO-PA."
    }
  }
}
