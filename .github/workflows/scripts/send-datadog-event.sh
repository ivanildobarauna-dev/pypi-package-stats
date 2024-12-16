curl -X POST "https://api.datadoghq.com/api/v2/events" \
-H "Accept: application/json" \
-H "Content-Type: application/json" \
-H "DD-API-KEY: ${DD_API_KEY}" \
-H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
-d @- << EOF
{
  "data": {
    "attributes": {
      "attributes": {
        "author": {
          "name": "github-actions",
          "type": "system"
        },
        "change_metadata": {
          "dd": {
            "team": "cloud_run_team",
            "user_email": "github-actions@yourdomain.com",
            "user_id": "github_actions_user",
            "user_name": "GitHub Actions"
          },
          "resource_link": "https://console.cloud.google.com/run/detail/prod/pypi-package-stats"
        },
        "changed_resource": {
          "name": "pypi-package-stats",
          "type": "cloud_run_service"
        },
        "impacted_resources": [
          {
            "name": "pypi-package-stats",
            "type": "cloud_run_service"
          }
        ],
        "new_value": {
          "revision": "rev-2",
          "status": "deployed",
          "region": "us-central1"
        },
        "prev_value": {
          "revision": "rev-1",
          "status": "inactive",
          "region": "us-central1"
        }
      },
      "category": "change",
      "message": "Deploy da aplicação 'pypi-package-stats' realizado com sucesso no ambiente 'prod'.",
      "tags": [
        "environment:prod",
        "application:pypi-package-stats",
        "event:deploy"
      ],
      "title": "Deploy do Cloud Run - pypi-package-stats (prod)"
    },
    "type": "event"
  }
}
EOF
