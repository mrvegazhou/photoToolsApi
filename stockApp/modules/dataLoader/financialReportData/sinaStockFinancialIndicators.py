# coding:utf8
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from io import StringIO
from ..config.stockDataConst import Constants, SinaConfig
from ...common.session import session


class SinaStockFinancialIndicators(object):
    '''
    获取个股历史报告期所有财务分析指标
    '''

    def __init__(self):
        self._session = session

    @property
    def financial_indicators_api(self) -> str:
        return Constants.STOCK_FINANCIAL_INDICATORS_URL.value

    def get_stock_financial_indicators(self, code):
        url = f"{self.financial_indicators_api.format(code, '2024')}"
        r = self._session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        year_context = soup.find(attrs={"id": "con02-1"}).find("table").find_all("a")
        year_list = [item.text for item in year_context]
        df = pd.DataFrame()
        for year in tqdm(year_list, leave=False):
            url = f"{self.financial_indicators_api.format(code, year)}"
            r = self._session.get(url)
            from_string = StringIO(r.text)
            temp_df = pd.read_html(from_string)[12].iloc[:, :-1]
            temp_df.columns = temp_df.iloc[0, :]
            temp_df = temp_df.iloc[1:, :]
            df0 = pd.DataFrame()
            indicator_list = ["每股指标", "盈利能力", "成长能力", "营运能力", "偿债及资本结构", "现金流量", "其他指标"]
            for i in range(len(indicator_list)):
                if i == 6:
                    inner_df = temp_df[
                               temp_df.loc[
                               temp_df.iloc[:, 0].str.find(indicator_list[i]) == 0, :
                               ].index[0]:
                               ].T
                else:
                    inner_df = temp_df[
                               temp_df.loc[temp_df.iloc[:, 0].str.find(indicator_list[i]) == 0, :]
                               .index[0]: temp_df.loc[
                                          temp_df.iloc[:, 0].str.find(indicator_list[i + 1]) == 0, :
                                          ]
                                          .index[0]
                                          - 1
                               ].T
                inner_df = inner_df.reset_index(drop=True)
                df0 = pd.concat([df0, inner_df], axis=1)
            df0.columns = df0.iloc[0, :].tolist()
            df0 = df0.iloc[1:, :]
            df0.index = temp_df.columns.tolist()[1:]
            df = pd.concat([df, df0])

        df.dropna(inplace=True)
        df.reset_index(inplace=True)
        df.rename(columns={'index': '日期'}, inplace=True)
        fields = ['日期', '摊薄每股收益(元)', '每股净资产_调整后(元)', '每股经营性现金流(元)',
                  '每股资本公积金(元)', '每股未分配利润(元)', '总资产(元)', '扣除非经常性损益后的净利润(元)',
                  '主营业务利润率(%)', '总资产净利润率(%)', '销售净利率(%)', '净资产报酬率(%)', '资产报酬率(%)',
                  '净资产收益率(%)', '加权净资产收益率(%)', '成本费用利润率(%)', '主营业务成本率(%)',
                  '应收账款周转率(次)', '存货周转率(次)', '固定资产周转率(次)', '总资产周转率(次)',
                  '流动资产周转率(次)', '流动比率', '速动比率', '现金比率(%)', '产权比率(%)', '资产负债率(%)',
                  '经营现金净流量对销售收入比率(%)', '经营现金净流量与净利润的比率(%)', '经营现金净流量对负债比率(%)',
                  '主营业务收入增长率(%)', '净利润增长率(%)', '净资产增长率(%)', '总资产增长率(%)']

        new_names = SinaConfig.financial_indicators_dict.value.keys()

        result = df[fields].rename(columns=dict(zip(fields, new_names)))
        return result