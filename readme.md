1. 爱德华·索普 凯利准则
2. 凯利公式还有一个变形：
f*=(p*rW-q*rL)/(rLrW)
其中f*,p,q同上，
rW：是获胜后的净赢率
rL：是净损失率。



3. 封装数据
   1. 实时数据
   2. 业绩报告
   3. 游资跟踪

4. 策略
   1. 拐点交易



已经开发出来的数据：
股票：
   股票日线  EastIntradayData->get_intraday_data
   股票板块查询   EastMarketRealTime->get_market_real_time('沪深xxxA')
   龙虎榜   EastDailyBillboard->get_daily_bill_board(开始日期， 结束日期)
   
基金：



qlib:
   mod init_instance_by_config
   |
   DatasetH init_instance_by_config 执行setup_data
   |
   -> Alpha158 里有个data_loader 
    -> DataHandlerLP 通过init_instance_by_config 处理数据 
    -> DataHandler DataHandlerLP的父类 通过init_instance_by_config调用QlibDataLoader 赋值给self.data_loader，
        setup_data调用lazy_sort_index，再通过self.data_loader调用load
        lazy_sort_index排序，
    -> QlibDataLoader load， 这个load方法在父父类DataLoader里，父类DLWParser重写load方法，
            load方法里包含load_group_df方法， 注意：这里DLWParser类有个循环执行load_group_df
            QlibDataLoader重写父类DLWParser的load_group_df方法
    -> load_group_df方法调用BaseProvider的features方法，features方法调用DatasetD.dataset
    -> LocalDatasetProvider datasetF 方法里调用
        get_instruments_d 调用LocalInstrumentProvider list_instruments
        get_column_names 调用DatasetProvider get_column_names
    LocalDatasetProvider dataset方法里dataset_processor inst_calculator 再调用LocalExpressionProvider的expression方法
    在LocalExpressionProvider类里
        expression = self.get_expression_instance(field) eval(parse_field(field)) 这个把方法和参数都转为ops类
        start_time = time_to_slc_point(start_time)
        end_time = time_to_slc_point(end_time)
    -> LocalExpressionProvider expression处理 register_all_ops已经加载了expression各种类
        util parse_field的方法正则
        Expression是这些ops的父类，有一个load方法，会调用_load_internal
        NpPairOperator继承PairOperator，实现_load_internal方法
        会执行到class Expression(abc.ABC) load方法

    qlib.data.base.Feature  $close   LocalFeatureProvider 从FileFeatureStorage的__getitem__方法里取值 
    qlib.data.ops.Abs   Abs(Sub($volume,Ref($volume,1)))

    所有的expression都要执行load方法，这个方法在Expression类中。位置在qlib/qlib/data/base.py
    再执行NpPairOperator类的_load_internal方法， Add Div都是继承NpPairOperator类的
    FeatureD.feature 是取数据用的 ---> localFeatureProvider feature ----> FileFeatureStorage __getitem__  读取bin文件

    ExpressionOps
        ElemOperator
            ChangeInstrument
            NpElemOperator
            TResample
        PairOperator
            NpPairOperator
        If
        Rolling
    
   
   DataLoader:
      C = QlibConfig(_default_config) 
        -> register_all_wrappers(self) -> register_wrapper(DatasetD, _dprovider, "qlib.data") -> LocalDatasetProvider
                                    |---> register_wrapper(D, C.provider, "qlib.data") -> LocalProvider
                                    |---> register_wrapper(Inst, _instrument_provider, "qlib.data") -> LocalInstrumentProvider -> list_instruments()
                                    |---> register_wrapper -> LocalCalendarProvider load_calendar -> backend_obj -> FileCalendarStorage (qlib.data.storage.file_storage)
                                    |---> LocalExpressionProvider 
                                    |---> LocalFeatureProvider


backtest:
    backtest方法




Alpha158初始化的时候要加载 QlibDataLoader 到 data_loader
的父类 执行 self.setup_data()  
 DLWParser 有 load
再执行QlibDataLoader load_group_df
    

                            
 LocalDatasetProvider dataset
 DatasetProvider  inst_calculator