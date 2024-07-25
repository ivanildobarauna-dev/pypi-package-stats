MERGE DW.PYPI_PROJ PROD USING (
SELECT
  FARM_FINGERPRINT(CONCAT(
    DATETIME_TRUNC(DATETIME_SUB(TIMESTAMP, INTERVAL 3 HOUR), HOUR),
    COUNTRY_CODE,
    DOWNS.PROJECT ,
    FILE.VERSION,
    IFNULL(UPPER(details.installer.name), "UNKNOWN") ,
    IFNULL(details.python, "UNKNOWN")
  )) ID,
  DATETIME_TRUNC(DATETIME_SUB(TIMESTAMP, INTERVAL 3 HOUR), HOUR) DTTM,
  COUNTRY_CODE,
  DOWNS.PROJECT ,
  FILE.VERSION PACKAGE_VERSION,
  IFNULL(UPPER(details.installer.name), "UNKNOWN") INSTALLER_NAME,
  IFNULL(details.python, "UNKNOWN") PYTHON_VERSION,
  COUNT(*) TOTAL_DOWNLOADS
  ,DATETIME_SUB(CURRENT_DATETIME("-03:00"), INTERVAL 3 HOUR) DTTM_INSERT
  ,DATETIME_SUB(CURRENT_DATETIME("-03:00"), INTERVAL 3 HOUR) DTTM_UPDATE
FROM
  `bigquery-public-data.pypi.file_downloads` DOWNS
WHERE
  TIMESTAMP_TRUNC(timestamp, DAY) >= TIMESTAMP(CURRENT_DATE("-03:00")-1)
  AND DOWNS.PROJECT IN ("currency-quote", "api-to-dataframe")
  and not details.installer.name = "bandersnatch"
  GROUP BY 1,2,3,4,5,6,7

  ) STG ON PROD.ID = STG.ID
  WHEN NOT MATCHED THEN INSERT VALUES (ID, DTTM, COUNTRY_CODE, PROJECT, PACKAGE_VERSION, INSTALLER_NAME, PYTHON_VERSION, TOTAL_DOWNLOADS, DTTM_INSERT, DTTM_UPDATE)
  WHEN MATCHED AND PROD.TOTAL_DOWNLOADS < STG.TOTAL_DOWNLOADS THEN UPDATE SET
    TOTAL_DOWNLOADS = STG.TOTAL_DOWNLOADS,
    DTTM_UPDATE = STG.DTTM_UPDATE