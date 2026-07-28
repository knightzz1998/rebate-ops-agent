# 数据库环境变量配置

# =============================================================================
# DEV 环境 (PostgreSQL)
# =============================================================================
export REBATE_PG_HOST="10.31.249.150"
export REBATE_PG_PORT="5432"
export REBATE_PG_USER="gksk_rebate_admin"
export REBATE_PG_PASSWORD="H:*#C5g=g9&6gHx1?QUO"
export REBATE_PG_DATABASE="gksk_rebate"

# =============================================================================
# SIT 环境 (PostgreSQL)
# =============================================================================
# export REBATE_PG_HOST="10.31.249.151"
# export REBATE_PG_PORT="5432"
# export REBATE_PG_USER="gksk_rebate_admin"
# export REBATE_PG_PASSWORD="Wy4Nwq:D;!N!5B7svj"
# export REBATE_PG_DATABASE="gksk_rebate"

# =============================================================================
# PROD 环境 (PostgreSQL)
# =============================================================================
# export REBATE_PG_HOST="10.160.8.200"
# export REBATE_PG_PORT="5432"
# export REBATE_PG_USER="gksk_rebate_user"
# export REBATE_PG_PASSWORD="7!tl+2ls@?cxSny@X9!,"
# export REBATE_PG_DATABASE="gksk_rebate"

# =============================================================================
# Doris (DEV/SIT/PROD 共用同一实例，暂时只配一套)
# =============================================================================
# export REBATE_DORIS_HOST="10.160.8.96"
# export REBATE_DORIS_PORT="9030"
# export REBATE_DORIS_USER="gksk_rebate_user"
# export REBATE_DORIS_PASSWORD="1TZcWXK#,yLdEOXobtD*"

# =============================================================================
# 使用方式: 取消注释要用的环境，source 此文件
#   source config/db_env.sh
# 或写入 ~/.zshrc 永久生效
#   cat config/db_env.sh >> ~/.zshrc
# =============================================================================
