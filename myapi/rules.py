import numpy as np
import pandas as pd
import datetime as dt
import time

class Rule:
    def __init__(self, df_list=None):
        self.list_of_rules = [
            # rule 0: sma10 cross-up sma20
            'self.get_sma_crossup(self.df_list, former="SMA10", latter="SMA20")',
            # rule 1: sma10 cross-up sma50
            'self.get_sma_crossup(self.df_list, former="SMA10", latter="SMA50")',
            # rule 2: adj close cross-up sma10
		    'self.get_adjclose_crossup_sma(self.df_list, sma="SMA10")',
            # rule 3: adj close cross-up sma20
		    'self.get_adjclose_crossup_sma(self.df_list, sma="SMA20")',
            # rule 4: adj close cross-up sma50
		    'self.get_adjclose_crossup_sma(self.df_list, sma="SMA50")',
            # rule 5: rsi cross-up 30
		    'self.get_rsi_crossup(self.df_list, th_rsi=30)',
            # rule 6: macd cross-up 
		    'self.get_macd_crossup(self.df_list, flag=0)',
            # rule 7: slow %k cross-up slow %d
		    'self.get_slowk_crossup(self.df_list)',
            # rule 8: adj close cross-down the BB lowerband
		    'self.get_adjclose_crossdown_BBlowerband(self.df_list)',
            # rule 9: sma10 > sma20
		    'self.get_sma_above(self.df_list, former="SMA10", latter="SMA20")',
            # rule 10: sma10 > sma50
		    'self.get_sma_above(self.df_list, former="SMA10", latter="SMA50")',
            # rule 11: sma20 > sma50
		    'self.get_sma_above(self.df_list, former="SMA20", latter="SMA50")',
            # rule 12: adj close > sma10
		    'self.get_adjclose_above_sma(self.df_list, sma="SMA10")',
            # rule 13: adj close > sma20
		    'self.get_adjclose_above_sma(self.df_list, sma="SMA20")',
            # rule 14: adj close > sma50
		    'self.get_adjclose_above_sma(self.df_list, sma="SMA50")',
            # rule 15: adj close > sma100
		    'self.get_adjclose_above_sma(self.df_list, sma="SMA100")',
            # rule 16: rsi < 80
		    'self.get_rsi_below(self.df_list, th_rsi=80)',
            # rule 17: macd hist > 0   (i.e. macd line > signal line)
		    'self.get_macdHist_above_0(self.df_list)',
            # rule 18: slow %k > slow %d
		    'self.get_slowk_above_slowd(self.df_list)'
            ]		# creates a new list for storing rules 
        self.df_list = df_list
		
    def add_rule(self, rule):
        self.list_of_rules.append(rule)
        print('{} is added'.format(rule))

    def update_df(self, df_list):
        self.df_list = df_list

    def run_rule(self, rule_no):
        print(self.list_of_rules[rule_no])
        return eval(self.list_of_rules[rule_no])

    def get_df(self):
        return self.df_list
		
    def get_num_of_rules(self):
        print(len(self.list_of_rules))
        return len(self.list_of_rules)
		
    def get_list_of_rules(self):
        print(self.list_of_rules)
        return self.list_of_rules
		
	# sma cross-up strategy
    def get_sma_crossup(self, df, former='SMA10', latter='SMA20', date=dt.datetime.today().strftime("%Y-%m-%d")):
        former_sma = df[former]
        latter_sma = df[latter]
        
        rule = (former_sma > latter_sma) & (former_sma.shift() < latter_sma.shift())

        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]

        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
        
        return results_df, b_flag

	# sma cross-down strategy
    def get_sma_crossdown(self, df, former='SMA10', latter='SMA20', date=dt.datetime.today().strftime("%Y-%m-%d")):
        former_sma = df[former]
        latter_sma = df[latter]
        
        rule = (former_sma < latter_sma) & (former_sma.shift() > latter_sma.shift())
        
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# adj close cross-up sma strategy
    def get_adjclose_crossup_sma(self, df, sma='SMA10', date=dt.datetime.today().strftime("%Y-%m-%d")):
        adj_close = df['Adj Close']
        sma = df[sma]
        
        rule = (adj_close > sma) & (adj_close.shift() < sma.shift())
        
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# adj close cross-down sma strategy
    def get_adjclose_crossdown_sma(self, df, sma='SMA10', date=dt.datetime.today().strftime("%Y-%m-%d")):
        adj_close = df['Adj Close']
        sma = df[sma]
        
        rule = (adj_close < sma) & (adj_close.shift() > sma.shift())
        
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
        
        return results_df, b_flag

	# rsi cross-up th_rsi
    def get_rsi_crossup(self, df, th_rsi=30, date=dt.datetime.today().strftime("%Y-%m-%d")):
        rsi = df['RSI14']
        
        rule = (rsi > th_rsi) & (rsi.shift() < th_rsi)
        
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# rsi cross-down th_rsi
    def get_rsi_crossdown(self, df, th_rsi=30, date=dt.datetime.today().strftime("%Y-%m-%d")):
        rsi = df['RSI14']
        
        rule = (rsi < th_rsi) & (rsi.shift() > th_rsi)
        
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# macd cross-up strategy
    def get_macd_crossup(self, df, flag=0, date=dt.datetime.today().strftime("%Y-%m-%d")):
		# flag == 0: both macd > 0 and macd < 0
		# flag == 1: only macd > 0
		# flag == 2: only macd < 0
        macd = df['MACD']
        macdHist = df['MACDhist']
        
        if flag == 0:
            rule = (macdHist > 0) & (macdHist.shift() < 0)
        elif flag == 1:
            rule = (macdHist > 0) & (macdHist.shift() < 0) & (macd > 0)
        else:
            rule = (macdHist > 0) & (macdHist.shift() < 0) & (macd < 0)
            
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# macd cross-down strategy
    def get_macd_crossdown(self, df, flag=0, date=dt.datetime.today().strftime("%Y-%m-%d")):
		# flag == 0: both macd > 0 and macd < 0
		# flag == 1: only macd > 0
		# flag == 2: only macd < 0
        macd = df['MACD']
        macdHist = df['MACDhist']
        
        if flag == 0:
            rule = (macdHist < 0) & (macdHist.shift() > 0)
        elif flag == 1:
            rule = (macdHist < 0) & (macdHist.shift() > 0) & (macd > 0)
        else:
            rule = (macdHist < 0) & (macdHist.shift() > 0) & (macd < 0)
            
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# slow %k cross-up slow %d strategy
    def get_slowk_crossup(self, df, date=dt.datetime.today().strftime("%Y-%m-%d")):
        slowk = df['Slowk']
        slowd = df['Slowd']
        
        rule = (slowk > slowd) & (slowk.shift() < slowd.shift())
        
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# slow %k cross-down slow %d strategy
    def get_slowk_crossdown(self, df, date=dt.datetime.today().strftime("%Y-%m-%d")):
        slowk = df['Slowk']
        slowd = df['Slowd']
        
        rule = (slowk < slowd) & (slowk.shift() > slowd.shift())
		
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# adj close cross-up BB upperband strategy
    def get_adjclose_crossup_BBupperband(self, df, date=dt.datetime.today().strftime("%Y-%m-%d")):
        adj_close = df['Adj Close']
        bbupperband = df['BBupperband']
        
        rule = (adj_close > bbupperband) & (adj_close.shift() < bbupperband.shift())
        
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# adj close cross-down BB lowerband strategy
    def get_adjclose_crossdown_BBlowerband(self, df, date=dt.datetime.today().strftime("%Y-%m-%d")):
        adj_close = df['Adj Close']
        bblowerband = df['BBlowerband']
        
        rule = (adj_close < bblowerband) & (adj_close.shift() > bblowerband.shift())
        
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# sma10 > sma20, or sma10 > sma50, etc.
    def get_sma_above(self, df, former='SMA10', latter='SMA20', date=dt.datetime.today().strftime("%Y-%m-%d")):
        former_sma = df[former]
        latter_sma = df[latter]
        
        rule = (former_sma > latter_sma) 
       
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# adj close > sma strategy
    def get_adjclose_above_sma(self, df, sma='SMA10', date=dt.datetime.today().strftime("%Y-%m-%d")):
        adj_close = df['Adj Close']
        sma = df[sma]
        
        rule = (adj_close > sma) 
        
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# macd hist > 0 strategy
    def get_macdHist_above_0(self, df, date=dt.datetime.today().strftime("%Y-%m-%d")):
        macdHist = df['MACDhist']
        
        rule = (macdHist > 0) 
        
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# rsi < th_rsi strategy
    def get_rsi_below(self, df, th_rsi=80, date=dt.datetime.today().strftime("%Y-%m-%d")):
        rsi = df['RSI14']
        rule = (rsi < th_rsi) 
        
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag

	# slow %k > slow %d strategy
    def get_slowk_above_slowd(self, df, date=dt.datetime.today().strftime("%Y-%m-%d")):
        slowk = df['Slowk']
        slowd = df['Slowd']
        
        rule = (slowk > slowd) 
        
        results_df = df.loc[rule]
        today_result = results_df.loc[results_df['Date'] == date]
        
        if not today_result.empty:
            b_flag = True
        else:
            b_flag = False
            
        return results_df, b_flag
		
