# EventMapping

This project is used to generate evolutionary relationship in *stakeholder layer* and *service & feature layer*.

## Rules:

### Common Rules
Please see source directly.

1. 若功能左侧紧靠利益相关者，则利益相关者可以提供该功能:
    * Generate: Actor|Recipient  --provide-->  Object
    * Remove: Object to simplify the pattern
    > 微软同意收购代码托管平台GitHub ==> GitHub provide 代码托管平台

2. 若句中实体数目少于一个则忽略该句
3. 基础模式Actor-Action-Recipient直接生成对应的边
