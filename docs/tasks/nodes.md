# アクションノード

- StartRun(float degree, float|null seconds)
    - プレイヤー向いている方向から反時計回りにdegree度方向へ走る
    - seconds秒間走る
    - secondsがnullの場合、止まるまで走り続ける
- StartRunTowards(string target, float degree, float|null seconds)
    - targetへの方向から反時計回りにdegree度方向へ走る
    - seconds秒間走る
    - secondsがnullの場合、止まるまで走り続ける
- StopRun
- Throw
    - ボールを投げる
- StartTurn(string direction, float|null seconds, float|null maxDegree)
    - direction方向に回転する
    - directionは"left"（反時計回り）または"right"（時計回り）
    - seconds秒間回転する
    - secondsがnullの場合、止まるまで回転し続ける
    - maxDegree度回転したら止まる
    - maxDegreeがnullの場合、無制限に回転し続ける
- StartTurnTowards(string target, float|null seconds)
    - targetに向かって回転する
    - seconds秒間回転する
    - secondsがnullの場合、targetに向かうまで回転し続ける
- StopTurn
- DoNothing
    - 何もしない

# コンディションノード

- AtFront(string target, float|null distance)
    - targetが真正面にdistance未満の距離に存在
- BallsMoreThanOrEquals(int number)
    - 所持しているボールがnumber以上
- InVisual(string target, float|null distance)
    - 正面方向（-60度 - +60度）に該当オブジェクトがdistance未満の距離に存在
- EnemyBallIncoming
    - 正面方向（-60度 - +60度）に、自機方向（偏角絶対値10度以内）に向かってきているボールが存在
- AfterSeconds(float seconds)
    - 前アクションノードを実行してからseconds経過
- IfRunning
    - 走っている
- IfTurning
    - 回っている
- AND
- OR
- NOT

# 変数

- Target
    - 正面方向（-60度 - +60度）にいる該当オブジェクト（下記）のうち一番近いものを返す
    - Enemy
    - Ally
    - BallDropped
    - BallThrownByEnemy
    - Wall
    - Obstacle

# 制御ノード

基本仕様: 毎Tickでアクションノードを選び直す

- Selector
    - 子のうち一番最初に実行可能なものを実行
- Sequence
    - 子を順次実行（フレームを越えてシーケンスを保持するが、Sequence外のノードが実行されたらリセット）