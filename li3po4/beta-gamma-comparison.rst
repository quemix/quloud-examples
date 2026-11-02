==============================
β相・γ相の結晶構造
==============================

Li・Ando らの `表II <https://doi.org/10.1063/1.4997242>`_ の結晶構造比較に、
本計算のCHGNetとOpenMX/PBEの格子定数を並べる。β相は16原子・2式量、
γ相は32原子・4式量の単位胞であり、体積は式量当たりに換算した。
本ページは構造量だけを比較し、全エネルギーや相安定性は評価しない。

.. raw:: html

   <table class="docutils align-center" style="width: auto; margin: 0 auto 1.5em;">
     <caption style="text-align: center;">文献表IIと本計算の格子定数</caption>
     <thead><tr><th>相</th><th>出典・手法</th><th>a (Å)</th><th>b (Å)</th><th>c (Å)</th><th>体積 (Å³/式量)</th></tr></thead>
     <tbody>
       <tr><th scope="rowgroup" rowspan="5">β相</th><td>文献NNP</td><td>4.914</td><td>5.287</td><td>6.164</td><td>80.07</td></tr>
       <tr><td>文献DFT-PBE</td><td>4.923</td><td>5.298</td><td>6.177</td><td>80.55</td></tr>
       <tr><td>実験</td><td>4.856</td><td>5.240</td><td>6.115</td><td>77.80</td></tr>
       <tr><td>本計算CHGNet</td><td>4.9439</td><td>5.3008</td><td>6.1517</td><td>80.61</td></tr>
       <tr><td>本計算OpenMX/PBE</td><td>4.9450</td><td>5.3168</td><td>6.2251</td><td>81.83</td></tr>
     </tbody>
     <tbody>
       <tr><th scope="rowgroup" rowspan="5">γ相</th><td>文献NNP</td><td>5.003</td><td>6.108</td><td>10.502</td><td>80.23</td></tr>
       <tr><td>文献DFT-PBE</td><td>5.001</td><td>6.177</td><td>10.615</td><td>81.98</td></tr>
       <tr><td>実験</td><td>4.927</td><td>6.120</td><td>10.490</td><td>79.08</td></tr>
       <tr><td>本計算CHGNet</td><td>4.9959</td><td>6.1820</td><td>10.6246</td><td>82.03</td></tr>
       <tr><td>本計算OpenMX/PBE</td><td>5.0429</td><td>6.2260</td><td>10.6680</td><td>83.74</td></tr>
     </tbody>
   </table>

格子定数・体積の実験値からの相対差は
:math:`100(x_{\mathrm{calc}}/x_{\mathrm{exp}}-1)`、
平均格子誤差は三軸の相対差の絶対値の平均である。

.. raw:: html

   <table class="docutils align-center" style="width: auto; margin: 0 auto 1.5em;">
     <caption style="text-align: center;">実験値に対する構造量の誤差</caption>
     <thead><tr><th>相</th><th>出典・手法</th><th>Δa (%)</th><th>Δb (%)</th><th>Δc (%)</th><th>ΔV (%)</th><th>平均 (%)</th></tr></thead>
     <tbody>
       <tr><th scope="rowgroup" rowspan="4">β相</th><td>文献NNP</td><td>+1.19</td><td>+0.90</td><td>+0.80</td><td>+2.92</td><td>0.96</td></tr>
       <tr><td>文献DFT-PBE</td><td>+1.38</td><td>+1.11</td><td>+1.01</td><td>+3.54</td><td>1.17</td></tr>
       <tr><td>本計算CHGNet</td><td>+1.81</td><td>+1.16</td><td>+0.60</td><td>+3.61</td><td>1.19</td></tr>
       <tr><td>本計算OpenMX/PBE</td><td>+1.83</td><td>+1.47</td><td>+1.80</td><td>+5.19</td><td>1.70</td></tr>
     </tbody>
     <tbody>
       <tr><th scope="rowgroup" rowspan="4">γ相</th><td>文献NNP</td><td>+1.54</td><td>−0.20</td><td>+0.11</td><td>+1.46</td><td>0.62</td></tr>
       <tr><td>文献DFT-PBE</td><td>+1.50</td><td>+0.93</td><td>+1.19</td><td>+3.67</td><td>1.21</td></tr>
       <tr><td>本計算CHGNet</td><td>+1.40</td><td>+1.01</td><td>+1.28</td><td>+3.74</td><td>1.23</td></tr>
       <tr><td>本計算OpenMX/PBE</td><td>+2.35</td><td>+1.73</td><td>+1.70</td><td>+5.89</td><td>1.93</td></tr>
     </tbody>
   </table>

本表で比較できる本計算uMLIPはCHGNetであり、UMA・SevenNetの
格子定数は未掲載である。実験値を基準にした平均格子誤差は、
β相・γ相で本計算CHGNetが
1.19%・1.23%、文献NNPが0.96%・0.62%である。本計算のほうが
それぞれ0.23・0.61ポイント大きい。体積誤差も本計算CHGNetの
+3.61%・+3.74%に対し、文献NNPは+2.92%・+1.46%である。
この2相の構造量では文献NNPのほうが実験値に近いが、
異なるモデルと最適化条件を含む比較であり、一般的な精度順位は示さない。

CHGNetの式量当たり体積は両相とも文献DFTとの差が約+0.07%である。
本計算OpenMX/PBEは文献DFTよりβ相で約+1.59%、γ相で約+2.15%大きく、
実験との差もCHGNetより大きい。この比較は提示された格子定数に基づく。
OpenMXの最終構造と最適化条件は、公開用の確定値とする前に確認が必要である。

まとめ
------

本計算CHGNetの平均格子誤差はβ相・γ相で1.19%・1.23%であり、
両相の構造を概ね再現するが、実験値への近さは文献NNPに及ばない。
この構造量の比較から、相安定性や拡散特性の精度までは判断できない。
