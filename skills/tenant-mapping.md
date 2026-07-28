# 租户编码与名称映射

## 已知映射

| 编码 | 名称 | schema |
|------|------|--------|
| 1006 | 国控宁夏 | gksk_rebate_account_1006 |
| 1010 | 国控青海 | gksk_rebate_account_1010 |
| 1014 | 国控北京 | gksk_rebate_account_1014 |
| 1109 | 国控江苏 | gksk_rebate_account_1109 |
| 1110 | 国控河南 | gksk_rebate_account_1110 |
| 1114 | 国控山东 | gksk_rebate_account_1114 |
| 1115 | 国控湖北 | gksk_rebate_account_1115 |
| 1116 | 国控湖南 | gksk_rebate_account_1116 |
| 1119 | 国控福建 | gksk_rebate_account_1119 |
| 1141 | 国控安徽 | gksk_rebate_account_1141 |
| 1143 | 国控江西 | gksk_rebate_account_1143 |
| 1164 | 国控四川 | gksk_rebate_account_1164 |
| 1168 | 国控陕西 | gksk_rebate_account_1168 |
| 1170 | 国控山西 | gksk_rebate_account_1170 |
| 1173 | 国控河北 | gksk_rebate_account_1173 |
| 1180 | 国控吉林 | gksk_rebate_account_1180 |
| 1181 | 国控辽宁 | gksk_rebate_account_1181 |
| 1183 | 国控黑龙江 | gksk_rebate_account_1183 |
| 1184 | 国控内蒙古 | gksk_rebate_account_1184 |
| 1196 | 国控新疆 | gksk_rebate_account_1196 |
| 1198 | 国控甘肃 | gksk_rebate_account_1198 |
| 1220 | 国药控股 | gksk_rebate_account_1220 |
| 1224 | 国控浙江 | gksk_rebate_account_1224 |
| 1226 | 国控云南 | gksk_rebate_account_1226 |
| 1228 | 国控广州 | gksk_rebate_account_1228 |
| 1229 | 国控贵州 | gksk_rebate_account_1229 |
| 1235 | 国控海南 | gksk_rebate_account_1235 |
| 1239 | 国控广西 | gksk_rebate_account_1239 |
| 1240 | 国控西藏 | gksk_rebate_account_1240 |

## 使用方式

Agent 在需要查询某个租户的数据时，先通过此映射获取 system_code 和 schema:

```
用户说: "查一下浙江的返利单"
Agent: lookup_tenant("浙江") → {"code": "1224", "name": "国控浙江", "schema": "gksk_rebate_account_1224"}
Agent: query_postgres("SELECT * FROM biz_sale_price_gap_order LIMIT 10", system_code="1224")
```
