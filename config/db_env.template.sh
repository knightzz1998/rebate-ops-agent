# 数据库环境变量配置模板
# 复制此文件为 db_env.sh，填入真实密码后执行

# =============================================================================
# DEV 环境 (PostgreSQL)
# =============================================================================
export REBATE_PG_HOST="<dev_host>"
export REBATE_PG_PORT="5432"
export REBATE_PG_USER="<dev_user>"
export REBATE_PG_PASSWORD="<dev_password>"
export REBATE_PG_DATABASE="gksk_rebate"

# =============================================================================
# SIT 环境 (PostgreSQL)
# =============================================================================
# export REBATE_PG_HOST="<sit_host>"
# export REBATE_PG_PORT="5432"
# export REBATE_PG_USER="<sit_user>"
# export REBATE_PG_PASSWORD="<sit_password>"
# export REBATE_PG_DATABASE="gksk_rebate"

# =============================================================================
# PROD 环境 (PostgreSQL)
# =============================================================================
# export REBATE_PG_HOST="<prod_host>"
# export REBATE_PG_PORT="5432"
# export REBATE_PG_USER="<prod_user>"
# export REBATE_PG_PASSWORD="<prod_password>"
# export REBATE_PG_DATABASE="gksk_rebate"

# =============================================================================
# Doris
# =============================================================================
# export REBATE_DORIS_HOST="<doris_host>"
# export REBATE_DORIS_PORT="9030"
# export REBATE_DORIS_USER="<doris_user>"
# export REBATE_DORIS_PASSWORD="<doris_password>"
