# -*- coding: utf-8 -*-
import uuid

YTO = 0


def wlb_waybill_i_get_response(package_id, express_company):
    waybill_code = str(uuid.uuid4()).split('-')[-1]
    return waybill_code, {
        "wlb_waybill_i_get_response": {
            "waybill_apply_new_cols": {
                "waybill_apply_new_info": [
                    {
                        "short_address": "SHANGHAI",
                        "trade_order_info": {
                            "package_id": package_id
                        },
                        "waybill_code": express_company + waybill_code,
                        "package_center_code": "VWMS_CENTER_CODE",
                        "package_center_name": "VWMS_CENTER_NAME",
                        "print_config": "VWMS_CONFIG",
                        "shipping_branch_code": "VWMS_1234",
                        "consignee_branch_name": "SHANGHAI_PUDONG",
                        "shipping_branch_name": "PUDONG_ZHANGJIANG",
                        "consignee_branch_code": "VWMS_4321"
                    }
                ]
            }
        }
    }


def wlb_waybill_i_cancel_response():
    return {
        "wlb_waybill_i_cancel_response": {
            "cancel_result": True
        }
    }


def wlb_waybill_i_search_response():
    return {
        "wlb_waybill_i_search_response": {
            "subscribtions": {
                "waybill_apply_subscription_info": [
                    {
                        "branch_account_cols": {
                            "waybill_branch_account": [
                                {
                                    "seller_id": 888888,
                                    "shipp_address_cols": {
                                        "waybill_address": [
                                            {
                                                "area": "朝阳区",
                                                "province": "北京",
                                                "town": "八里庄",
                                                "address_detail": "朝阳路高井，财满街，财经中心9号楼21单元6013",
                                                "city": "北京市",
                                                "waybill_address_id": 123
                                            }
                                        ]
                                    },
                                    "quantity": 123,
                                    "allocated_quantity": 123,
                                    "branch_code": "1321",
                                    "print_quantity": 32,
                                    "cancel_quantity": 10,
                                    "branch_name": "杭州余杭分部"
                                }
                            ]
                        },
                        "cp_type": 123,
                        "cp_code": "STO"
                    }
                ]
            }
        }
    }


def yto_response():
    code = str(uuid.uuid4()).split('-')[-1]
    return '''<Response>
    <logisticProviderID>YTO</logisticProviderID>
    <txLogisticID>WP15183117908113</txLogisticID>
    <clientID>K21000119</clientID>
    <mailNo>{}</mailNo>
    <distributeInfo>
        <shortAddress>300-006-000</shortAddress>
        <consigneeBranchCode>210185</consigneeBranchCode>
        <packageCenterCode>210901</packageCenterCode>
        <packageCenterName>上海转运中心</packageCenterName>
    </distributeInfo><code>200</code>
    <success>true</success>
</Response>'''.format(code)


def yto_response_missing_1():
    code = str(uuid.uuid4()).split('-')[-1]
    return '''<Response>
    <logisticProviderID>YTO</logisticProviderID>
    <txLogisticID>WP15183117908113</txLogisticID>
    <clientID>K21000119</clientID>
    <mailNo>{}</mailNo>
    <distributeInfo>
        <shortAddress>300-006 000</shortAddress>
        <consigneeBranchCode></consigneeBranchCode>
        <packageCenterCode></packageCenterCode>
        <packageCenterName></packageCenterName>
    </distributeInfo><code>200</code>
    <success>true</success>
</Response>'''.format(code)


def yto_response_missing_2():
    code = str(uuid.uuid4()).split('-')[-1]
    return '''<Response>
    <logisticProviderID>YTO</logisticProviderID>
    <txLogisticID>WP15183117908113</txLogisticID>
    <clientID>K21000119</clientID>
    <mailNo>{}</mailNo>
    <distributeInfo>
        <shortAddress></shortAddress>
        <consigneeBranchCode></consigneeBranchCode>
        <packageCenterCode></packageCenterCode>
        <packageCenterName></packageCenterName>
    </distributeInfo><code>200</code>
    <success>true</success>
</Response>'''.format(code)
