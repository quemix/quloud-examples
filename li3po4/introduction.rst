.. _li3po4-doc-introduction:

導入
====

非晶質Li₃PO₄（リン酸リチウム）は、薄膜電池などに使われる固体電解質です。
結晶のように同じ原子配列が繰り返されないため、Liイオンの移動しやすさは周囲の原子配置によって変わります。
この連載ではQuloudを使い、**Liがどの経路を通るか** と **温度を上げるとどれだけ速く拡散するか** を調べます。

計算で調べること
----------------

* :numref:`{number}. {name} <li3po4-doc-beta-gamma-comparison>` で結晶の格子定数を文献のDFT計算値と実験値に比べ、 :numref:`{number}. {name} <li3po4-doc-melt-quench-structure>` でγ相を溶融・急冷して32原子の不規則構造を作ります。
* :numref:`{number}. {name} <li3po4-doc-vacancy-formation>` でLiを1個取り除くのに必要なエネルギーを求めます。隣のLiが空いた位置に移る経路と、経路上で越えるエネルギー障壁を :numref:`{number}. {name} <li3po4-doc-vacancy-paths>` と :numref:`{number}. {name} <li3po4-doc-vacancy-barriers>` で調べます。
* :numref:`{number}. {name} <li3po4-doc-lithium-msd>` と :numref:`{number}. {name} <li3po4-doc-diffusivity-temperature>` では、Li空孔を1つ含む31原子モデルを用います。分子動力学（MD）でLiの位置を時間に沿って追い、平均二乗変位から拡散係数を求めます。 :numref:`{number}. {name} <li3po4-doc-partial-rdf>` では、原子対の距離分布から局所構造の温度変化を調べます。
* :numref:`{number}. {name} <li3po4-doc-large-structure-rdf>` では、125～2012原子のモデルで原子配置と距離分布を比べます。 :numref:`{number}. {name} <li3po4-doc-large-model-diffusivity>` では、1006原子モデルで拡散の温度依存性を評価します。

比較に使う計算手法
------------------

Liらは、Li₃PO₄の密度汎関数理論（DFT）データで学習したニューラルネットワークポテンシャル（NNP）を使い、構造とLi拡散を調べました。
この連載では、OpenMXによるDFTと、事前学習済みの3つの汎用\ `機械学習原子間ポテンシャル <https://technical-notes.quemix.com/md/mlip.html>`__\ （UMA、SevenNet、CHGNet）を使います。使用する手法は計算項目によって異なります。各記事では、Liらのモデルと計算値を「文献NNP」「文献DFT」と表記します。

1006原子モデルでは、Li拡散の活性化エネルギーはCHGNetで0.296 eV、文献NNPで0.55 eVでした。
空孔の平均移動障壁は、3つのモデルの中でUMA（0.50 eV）が文献値に最も近い値を示しました。
個々の移動障壁の精度を評価するには構造と経路をそろえる必要があり、拡散係数の精度を評価するにはMDの条件もそろえる必要があります。

参考文献
--------

Wenwen Li, Yasunobu Ando, Emi Minamitani, Satoshi Watanabe,
“Study of Li atom diffusion in amorphous Li₃PO₄ with neural network potential,”
*J. Chem. Phys.* **147**, 214106 (2017).
`DOI: 10.1063/1.4997242 <https://doi.org/10.1063/1.4997242>`__.
