# Nano Cortex FAQs 8–40, translated from neuraldsp.com/nano-cortex (Nov 2026). Questions 1–7 already exist in the template.
def ul(*items): return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
def p(*paras): return ''.join(f'<p>{x}</p>' for x in paras)

NANO_FAQ = [
 ('アンプモデルとNeural Captureの違いは何ですか？', p(
   'プラグインや Quad Cortex に搭載されているアンプモデルは、アンプのさまざまな設定における全体的な挙動を詳細に分析・モデリングして作られています。コントロールの位置ごとにアンプからデータを収集し、機械学習によって全レンジにわたるサウンドと弾き心地を再現します。',
   '一方、Neural Capture は、特定のアンプ、キャビネット、ペダルの「現在の設定」でのサウンドと弾き心地を正確に再現し、その個体ならではの細かな特性まで捉えます。',
   'Neural Capture は Nano Cortex と Quad Cortex のどちらでもご自身で作成でき、お手持ちの機材を圧倒的なリアルさでデジタル化できます。')),
 ('シグナルチェーンのNeural Captureスロットには何を読み込めますか？', p(
   'Nano Cortex の Neural Capture スロットには Neural Capture を読み込みます。Neural Capture は、アンプ、キャビネット、ドライブペダルをキャプチャーしたデジタルレプリカです。Cortex Cloud では何千もの Neural Capture を無料で利用でき、Cortex Cloud アプリからワイヤレスで Nano Cortex に読み込めます。',
   'Nano Cortex にあらかじめ収録されている 25 種類の Neural Capture に加えて、最大 256 個の Neural Capture を保存し、Cortex Cloud アプリで管理できます。')),
 ('Nano CortexにはNeural Captureをいくつ保存できますか？', p('Nano Cortex には最大 256 個の Neural Capture を保存できます。')),
 ('Neural Captureの作成にはどんな機材が必要ですか？', p('キャプチャーする対象によって異なります。') + ul(
   'ドライブペダル：楽器用ケーブルのみで作成できます。',
   'アンプ＋キャビネット、またはコンボアンプ：サウンドを収録するマイクが必要です。ダイナミックマイクは Nano Cortex に直接接続できます。コンデンサーマイクの場合は外部プリアンプが必要です。',
   'スピーカーのないアンプヘッド：アンプヘッドをリアクティブロードボックスに接続し、その信号を Nano Cortex に送ってキャプチャーします。') + p(
   'キャプチャーの処理はすべて本体だけで完結します。Neural Capture の作成にコンピューター、インターネット、Cortex Cloud アプリへの接続は必要ありません。')),
 ('キャプチャー入力はコンデンサーマイク用のファンタム電源に対応していますか？', p('いいえ。キャプチャー入力は 48V ファンタム電源を供給しません。コンデンサーマイクを使用する場合は外部プリアンプが必要です。')),
 ('Nano CortexとQuad Cortexで作成したNeural Captureに違いはありますか？', p('Nano Cortex と Quad Cortex で作成した Neural Capture の解像度と品質は同じです。どちらも同じ技術で、アンプ、キャビネット、ペダルの本物のサウンドと弾き心地を捉えます。Nano Cortex で作成した Neural Capture は Quad Cortex に読み込むことができ、その逆も可能です。')),
 ('Neural Captureの作成にインターネット接続やコンピューターは必要ですか？', p('いいえ。コンピューター、インターネット、Cortex Cloud アプリへの接続は不要です。処理はすべてペダル本体の中で完結します。')),
 ('Neural Captureの作成にはどのくらい時間がかかりますか？', p('Neural Capture の作成にかかる時間は約 5 分です。')),
 ('どんな機材のNeural Captureを作成できますか？', p('あらゆるアンプ、キャビネット、ドライブペダルの Neural Capture を作成できます。')),
 ('Nano Cortexにはどんなデバイスが収録されていますか？', p('Nano Cortex には以下のデバイスが収録されています。') +
   '<p><strong>Neural Capture</strong></p>' + ul('ギターアンプ 20 種類', 'ベースアンプ 5 種類') +
   '<p><strong>キャビネット</strong></p>' + ul('ギターキャビネット 8 種類', 'ベースキャビネット 2 種類') +
   p('<strong>エフェクト／ユーティリティ</strong>：合計 50 種類以上。各デバイスはシグナルチェーン内の決まったスロットで使用できるよう設計されています。') +
   '<p><strong>インプットゲート</strong></p>' + ul('インプットゲートはシグナルチェーンの先頭、プリエフェクトスロットの前にあります。プリエフェクトスロットを使わずにノイズゲートを使用できます。') +
   '<p><strong>すべてのプリ／ポストエフェクトスロットで使用可能</strong></p>' + ul('EQ（3）：Parametric-3、Low-High Cut、Graphic-9') +
   '<p><strong>プリエフェクトスロットで使用可能</strong></p>' + ul(
     'Utility（3）：Adaptive Gate、Utility Gate、Volume',
     'Compressor（4）：Legendary 87 (M) - Universal Audio® 1176® ベース、Solid State Comp (M) - SSL® Bus ベース、VCA Comp (M)、Opto Comp (M)',
     'Wah（4）：Bubba Wah - Dunlop® Budda Budwah® ベース、Bass Wah、Crying Wah - Dunlop® Cry Baby® GCB-95® ベース、Crying Clyde Wah - Dunlop® Cry Baby® Clyde McCoy® ベース',
     'Filter（2）：Love Meat - Lovetone® Meatball® ベース、Envelope Filter',
     'Guitar Overdrive（9）：Obsessive Drive - Fulltone® OCD® ベース、OD250 - DOD® Overdrive Preamp 250® ベース、Rodent Drive - ProCo® Rat® ベース、Exotic - Xotic® BB Preamp® ベース、Chief OD1 - BOSS® OD-1® ベース、Chief BD2 - BOSS® BD-2® ベース、Facial Fuzz - Dunlop® Fuzzface® ベース、Exotic Z Boost - Xotic® RC Booster® ベース、Green 808 - Ibanez® TS808® ベース',
     'Bass Overdrive（2）：Microtubes B3K - Darkglass® Microtubes B3K® ベース、Exotic Bass Z Boost - Xotic® RC Bass Booster® ベース') +
   '<p><strong>プリエフェクトスロット 1 のみ</strong></p>' + ul('Pitch（1）：Transpose') +
   '<p><strong>ポストエフェクトスロットで使用可能</strong></p>' + ul('Compressor（4）：Legendary 87 (ST) - Universal Audio® 1176® ベース、Solid State Comp (ST) - SSL® Bus ベース、VCA Comp (ST)、Opto Comp (ST)') +
   '<p><strong>ポストエフェクトスロット 1 のみ</strong></p>' + ul('Utility（1）：Doubler',
     'Modulation（7）：MX Flanger - MXR® Flanger M117R® ベース、Dream Chorus (ST) - TC Electronic® Dreamscape® ベース、Chorus 229T - TC Electronic® TC-2290® ベース、Chief CE2W (ST) - BOSS® CE-2W® ベース、Chief DC2W (ST) - BOSS® DC-2W® Dimension ベース、MX Phase 95 - MXR® Phase 95® ベース、MX Vibes - MXR® UniVibe® ベース') +
   '<p><strong>ポストエフェクトスロット 2 のみ</strong></p>' + ul('Delay（6）：Tape Delay (ST)、Analog Delay (ST)、Digital Delay (ST)、Dual Delay、Dual Reverse Delay、Circular Delay') +
   '<p><strong>ポストエフェクトスロット 3 のみ</strong></p>' + ul('Reverb（6）：Room、Hall、Modulated、Ambience、Cave、Mind Hall - Lexicon® 224® ベース') +
   p('さらに Cortex Cloud を無料で利用でき、アンプ、キャビネット、ドライブペダルの何千ものキャプチャーを探して、ワイヤレスで読み込めます。')),
 ('プリセットとは何ですか？', p('Nano Cortex のプリセットは、シグナルチェーン全体の設定を保存するもので、お気に入りのトーンをすばやく簡単に呼び出せます。Nano Cortex には最大 64 個のプリセットを保存できます。初期設定の 4 プリセットモードでは、フットスイッチ I と II で 4 つのプリセットにすばやくアクセスできます。')),
 ('Quad CortexのプリセットをNano Cortexで読み込めますか？', p('いいえ。Nano Cortex のシグナルチェーンは固定のため、Quad Cortex のプリセットとは互換性がありません。')),
 ('Nano CortexのIRローダーが業界屈指といわれる理由は？', p(
   'Nano Cortex の IR ローダーは、スタジオグレードの高品質なインパルスレスポンス（IR）と豊富なカスタマイズ性により、業界でも屈指の性能を備えています。',
   'Nano Cortex には 10 種類のキャビネットモデルが搭載され、それぞれに複数の IR が用意されています。キャビネットごとに 5 種類のマイクと、マイクごとに 6 つのマイクポジションを選べるため、1 つのキャビネットモデルにつき 30 種類（5 マイク × 6 ポジション）の IR があります。10 モデルで合計 300 種類のスタジオ品質 IR となり、音作りの可能性は無限に広がります。',
   'さらに最大 256 個のカスタム IR を保存でき、極めてリアルで自由度の高いキャビネットシミュレーションが可能です。')),
 ('Nano Cortexでギター／ベースのチューニングをデジタルで変更できますか？', p('はい。内蔵の Transpose エフェクトで、体感できる遅延なしに瞬時にチューニングを変更できます。')),
 ('サードパーティ製のインパルスレスポンス（IR）は使えますか？', p('はい。あらかじめ収録された 300 種類の IR に加えて、最大 256 個のカスタム IR をアップロードして保存できます。')),
 ('プリセット切り替え時に音切れはありますか？', p('NanOS 2.0.0 以降、プリセット切り替え時にごく短い音切れが発生します。通常は約 60 ミリ秒とごくわずかで、ディレイやリバーブの残響は途切れず、プリセット間で自然に続きます。この変更により、シグナルチェーンの自由度が高まり、NanOS 2.0.0 で追加された新機能や新デバイスを搭載できるようになりました。')),
 ('Nano Cortexのノブやスイッチが反応しないのはなぜですか？', p(
   'ノブやスイッチを操作しても反応しない場合は、「Parameter Lock（パラメーターロック）」機能が有効になっている可能性があります。この機能はライブ中の誤操作を防ぐため、ノブとフットスイッチのロータリー操作を無効にします。',
   'Parameter Lock のオン／オフは、EXIT ボタンを 3 秒間長押しして切り替えます。有効な間は EXIT の LED リングが点灯します。')),
 ('Nano Cortexはオーディオインターフェースとして使えますか？', p('はい。Nano Cortex は本格的な低レイテンシーのオーディオインターフェースとして機能し、24bit / 48kHz、7 チャンネル（4 イン / 3 アウト）の USB オーディオに対応しています。')),
 ('オーディオインターフェースとして対応しているDAWは？', p('Nano Cortex は主要な DAW すべてに対応しています。') + ul(
   'Ableton Live（バージョン 10 以降）', 'Cakewalk（2018 以降）', 'Cubase（バージョン 6 以降）', 'GarageBand（バージョン 10 以降）', 'Logic Pro（バージョン 10 以降）',
   'Pro Tools（バージョン 12 以降）', 'REAPER（バージョン 6 以降）', 'Studio One Artist（バージョン 5 以降）', 'Studio One Professional（バージョン 2 以降）', 'FL Studio（バージョン 21 以降）')),
 ('どんなモニター機器に接続できますか？', p('Nano Cortex は、スタジオモニター、FRFR キャビネット、アンプ、ペダルボードなど、あらゆるセットアップに組み込めます。') + ul(
   'スタジオモニター、FRFR キャビネット、PA システム：OUTPUT 1L と OUTPUT 2R から接続します。',
   'ギター／ベースアンプ：OUTPUT 1L をアンプの入力に接続するか、アンプのエフェクトループのリターンに接続します。',
   'ギター／ベースキャビネット：外部パワーアンプを経由して接続します。',
   'ペダル：1/4" 入力と OUTPUT 1L / 2R を使ってペダルボードに組み込めます。')),
 ('IRローダーのグローバルバイパス機能とは？', p('IR Loader Global Bypass 機能を使うと、すべてのプリセットで IR ローダーをまとめてバイパスできます。')),
 ('XLRケーブルは使えますか？', p('はい。Nano Cortex の出力はバランス TRS のため、TRS-XLR ケーブルを使っても XLR 同士で接続した場合と比べて音質が損なわれることはありません。XLR 出力が必要なセットアップでは、市販の TRS-XLR ケーブルで簡単に対応できます。')),
 ('ペダルボードで使えますか？', p('はい。Nano Cortex は既存のセットアップにシームレスに組み込めるよう設計されています。アンプとキャビネットの代わりとしても、ストンプボックス／マルチエフェクターとしても使用できます。1/4" 入力と OUTPUT 1L / 2R を使って、シグナルチェーンの好きな位置に配置できます。')),
 ('エフェクトループはありますか？', p('いいえ。Nano Cortex には専用のエフェクトループはありません。ただし、1/4" 楽器入力と OUTPUT 1L / 2R を使ってペダルボードに組み込むことができます。')),
 ('ステレオで使えますか？', p('Nano Cortex はモノラル入力・ステレオ出力のデバイスです。デュアル TRS 出力を備え、スタジオモニター、PA システム、FRFR キャビネットなどのステレオ環境に接続できます。')),
 ('USB-Cから給電できますか？', p('はい。Nano Cortex は USB-C（5V / 1.5A）から給電できます。付属の USB-C ケーブルで、コンピューターやモバイルバッテリーなど USB-C 対応の電源に接続してください。')),
 ('Quad Cortexの電源アダプターでNano Cortexを使えますか？', p('はい。Quad Cortex の電源アダプターは Nano Cortex に対応しています。')),
 ('Nano Cortexをワイヤレスで操作できますか？', p('はい。Cortex Cloud アプリからワイヤレスで操作できます。シグナルチェーン内のバーチャルデバイスのパラメーター調整や、Neural Capture、プリセット、IR、本体設定の管理が可能です。')),
 ('Bluetoothでオーディオをストリーミングしたり、ワイヤレスヘッドフォンを使ったりできますか？', p('いいえ。Bluetooth は Nano Cortex と Cortex Cloud アプリのペアリング専用です。')),
 ('MIDI機器やエクスプレッションペダルで操作できますか？', p('はい。MIDI TRS 入力から MIDI フットスイッチやエクスプレッションペダルを接続できます。')),
 ('MIDIアウトに対応していますか？', p('Nano Cortex は USB-C 経由で MIDI イン／アウトに対応しています。EXP/MIDI TRS 端子は MIDI イン専用です。')),
 ('ファームウェアのアップデート方法は？', p('Nano Cortex のファームウェアアップデートは Cortex Cloud アプリで行います。アップデートの確認から最新バージョンのワイヤレスインストールまで簡単に行えます。')),
 ('Nano Cortex用のデスクトップアプリはありますか？', p('Nano Cortex 用のデスクトップコントローラーは提供されていません。')),
]
