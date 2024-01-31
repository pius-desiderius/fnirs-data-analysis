#define your filtering parameters

LFREQ = 0.05
HFREQ = 0.1
H_TRANS_BANDWIDTH = 0.1
L_TRANS_BANDWIDTH = 0.05

METHOD = 'fir'
F_TYPE = 'butter'
ORDER = 10
RIPPLE = 1.0
FIR_DESIGN='firwin2'

IIR_FILTER_PARAMS = dict(
                          order=ORDER, 
                          ftype=F_TYPE,
#                           rp=RIPPLE
                          )


if METHOD == 'iir':
    FILTER_DICT = dict(
                        l_freq=LFREQ, 
                        h_freq=HFREQ,                     
                        method=METHOD, 
                        iir_params=IIR_FILTER_PARAMS, 
                        verbose=False,
                      )

elif METHOD == 'fir':
    FILTER_DICT = dict(
                        l_freq=LFREQ, 
                        h_freq=HFREQ, 
                        method=METHOD,
                        h_trans_bandwidth=H_TRANS_BANDWIDTH,
                        l_trans_bandwidth=L_TRANS_BANDWIDTH,
                        fir_design=FIR_DESIGN,
                        verbose=False,
                      )