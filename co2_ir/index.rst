CO₂の赤外スペクトル
===========================================

第一原理分子動力学で得たCO₂分子の運動からスペクトルを求め、計算手法による違いと実験値を比較します。

.. container:: case-actions

   * :doc:`計算結果を読む <ir_spectrum>`
   * :doc:`計算条件と再現手順 <reproduction>`

.. container:: case-preview

   .. image:: figures/spectra.png
      :alt: CPMDで求めた双極子モーメントと振動座標のパワースペクトル
      :width: 100%

   CPMDで求めたパワースペクトルでは、1200〜1300 cm⁻¹付近に対称伸縮振動のピークが\
   振動座標（右）に現れますが、双極子モーメント（左）には対応するピークが見られず、\
   対称伸縮振動が赤外不活性であることが分かります。

.. toctree::
   :hidden:

   ir_spectrum
   reproduction
