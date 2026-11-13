"""Render four portfolio figures from committed JSON results.

Optional development dependency: pip install -r requirements-visuals.txt
The analysis programs and tests require only the Python standard library.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, StrMethodFormatter

ROOT=Path(__file__).resolve().parent
BLUE='#2463a6';TEAL='#14856e';RED='#bc4b51';INK='#182c43';MUTED='#5a6d82'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
    'axes.spines.right':False,'axes.labelcolor':INK,'text.color':INK,'xtick.color':MUTED,
    'ytick.color':MUTED,'axes.edgecolor':'#c5cfdb','figure.facecolor':'white',
    'axes.titleweight':'bold','axes.titlepad':18,'savefig.dpi':150})


def load(slug):
    folder=ROOT/'projects'/slug
    return folder,json.loads((folder/'results.json').read_text())


def save(fig, folder, note):
    fig.text(.07,.035,'SYNTHETIC CASE STUDY  |  '+note,fontsize=8,color=MUTED)
    fig.savefig(folder/'preview.png',facecolor='white')
    plt.close(fig)
    print(folder.name+'/preview.png')


def revenue():
    folder,data=load('12-subscription-revenue-bridge')
    bridge=data['bridges'][-1];m=bridge['movements_cents']
    labels=['Opening','New','Reactivated','Expansion','Contraction','Churn','Closing']
    changes=[bridge['opening_mrr_cents'],m['new'],m['reactivation'],m['expansion'],-m['contraction'],-m['churn'],bridge['closing_mrr_cents']]
    fig,ax=plt.subplots(figsize=(10,5.4));fig.subplots_adjust(left=.1,right=.97,top=.8,bottom=.2)
    running=0
    for i,value in enumerate(changes):
        if i in (0,len(changes)-1):
            bottom=0;height=value;color=BLUE
            running=value
        else:
            before=running;running+=value
            bottom=min(before,running);height=abs(value);color=TEAL if value>=0 else RED
        ax.bar(i,height,bottom=bottom,color=color,width=.65,zorder=3)
        label=f'{value:+,}' if 0<i<len(changes)-1 else f'{value:,}'
        ax.annotate(label,(i,bottom+height),xytext=(0,7),textcoords='offset points',ha='center',fontsize=9)
        if i<len(changes)-1:
            ax.plot([i+.325,i+.675],[running,running],color='#9baabc',linewidth=1)
    ax.set_xticks(range(len(labels)),labels);ax.set_ylabel('MRR (integer minor units)')
    ax.set_ylim(0,max(changes+[bridge['closing_mrr_cents']])*1.3)
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'));ax.grid(axis='y',alpha=.15,zorder=0)
    ax.set_title('October MRR bridge: growth includes returning customers',loc='left', y=1.16)
    fig.text(.1,.86,f"Existing-account net retention: {bridge['net_revenue_retention']:.1%}  |  Bridge difference: {bridge['bridge_difference_cents']} minor units",fontsize=10,color=MUTED)
    save(fig,folder,'MRR movement is not cash flow or recognized revenue.')


def forecast():
    folder,data=load('16-demand-forecast-backtest');points=data['holdout_predictions']
    fig,ax=plt.subplots(figsize=(10,5.4));fig.subplots_adjust(left=.1,right=.97,top=.8,bottom=.2)
    x=list(range(len(points)))
    ax.plot(x,[p['actual'] for p in points],color=BLUE,marker='o',label='Observed demand',linewidth=2)
    ax.plot(x,[p['forecast'] for p in points],color=TEAL,marker='s',linestyle='--',label='One-day-ahead forecast',linewidth=2)
    ax.set_xticks(x,[p['date'][5:] for p in points]);ax.set_xlabel('Holdout date (2026)');ax.set_ylabel('Units')
    ax.set_ylim(0,max(p['actual'] for p in points)*1.25);ax.grid(axis='y',alpha=.15)
    ax.legend(frameon=False,loc='upper left');ax.set_title('Demand forecast: an untouched week after model selection',loc='left', y=1.16)
    fig.text(.1,.86,f"Selected on validation: {data['selected_model']}  |  Holdout MAE: {data['holdout_score']['mae']:.2f} units  |  WAPE: {data['holdout_score']['wape']:.1%}",fontsize=10,color=MUTED)
    save(fig,folder,'Rolling one-day-ahead evaluation; no future observations enter a forecast.')


def queue():
    folder,data=load('17-service-queue-simulation');scenarios=data['scenarios'];x=list(range(len(scenarios)))
    fig,ax=plt.subplots(figsize=(10,5.4));fig.subplots_adjust(left=.1,right=.97,top=.8,bottom=.2)
    for shift,key,label,color in [(-.18,'mean_wait_minutes','Mean wait',BLUE),(.18,'p90_wait_minutes','90th percentile wait',TEAL)]:
        bars=ax.bar([i+shift for i in x],[s[key] for s in scenarios],width=.34,label=label,color=color)
        ax.bar_label(bars,fmt='%.1f',padding=4)
    ax.set_xticks(x,[str(s['workers'])+' worker'+('s' if s['workers']>1 else '') for s in scenarios])
    ax.set_ylabel('Queue waiting time (minutes)');ax.set_ylim(0,200);ax.legend(frameon=False)
    ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    ax.set_title('Same workload, different parallel handling capacity',loc='left', y=1.16)
    fig.text(.1,.86,'40 synthetic tickets | First-come-first-served | No shifts, breaks, or task priorities',fontsize=10,color=MUTED)
    save(fig,folder,'Scenario comparison only; this does not establish optimal staffing.')


def mix():
    folder,data=load('20-campaign-mix-adjustment')
    fig,ax=plt.subplots(figsize=(10,5.4));fig.subplots_adjust(left=.1,right=.97,top=.8,bottom=.2)
    for shift,variant,color in [(-.18,'control',BLUE),(.18,'treatment',TEAL)]:
        values=[data['pooled_rates'][variant],data['standardized_rates'][variant]]
        bars=ax.bar([shift,1+shift],values,width=.34,label=variant.title(),color=color)
        ax.bar_label(bars,labels=[f'{v:.1%}' for v in values],padding=4)
    ax.set_xticks([0,1],['Raw pooled rates\nDifferent segment mixes','Standardized rates\nSame combined segment mix'])
    ax.set_ylim(0,.7);ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylabel('Conversion rate')
    ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True);ax.legend(frameon=False)
    ax.set_title('A campaign conclusion reverses after a common-mix comparison',loc='left', y=1.16)
    fig.text(.1,.86,f"Raw difference: {data['pooled_difference']*100:+.1f} percentage points  |  Standardized difference: {data['standardized_difference']*100:+.1f} points",fontsize=10,color=MUTED)
    save(fig,folder,'Descriptive standardization; does not establish a causal treatment effect.')


if __name__=='__main__':
    revenue();forecast();queue();mix()
