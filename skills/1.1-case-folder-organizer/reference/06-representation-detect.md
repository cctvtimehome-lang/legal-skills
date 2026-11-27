# 代理方向判断逻辑(跨 skill 共享规则)

> ⚠️ 本规则为跨 skill 共享规则,适用于所有需要判断代理方向的 skill(cn-litigation、smart-archive-checker、case-pleadings 等)。 实现时应提升为全局规则库条目。

---

## 一审阶段

**触发时机**:`1.起诉状和证据` 目录首次出现文件时

```
IF  1.起诉状和证据/起诉状_姓名.docx  存在
THEN  一审代理方向 = 原告

IF  起诉状_姓名.docx 不存在,且 起诉状_姓名.pdf 存在
THEN  一审代理方向 = 被告
```

---

## 二审阶段

**触发时机**:`5.上诉状和证据` 目录首次出现文件时

```
IF  5.上诉状和证据/上诉状_姓名.docx  存在
THEN  二审代理方向 = 上诉人

IF  上诉状_姓名.docx 不存在,且 上诉状_姓名.pdf 存在
THEN  二审代理方向 = 被上诉人
```

---

## 再审阶段

**触发时机**:`8.再审申请和证据` 目录首次出现文件时

```
IF  8.再审申请和证据/再审申请书_姓名.docx  存在
THEN  再审代理方向 = 申请再审方

IF  再审申请书_姓名.docx 不存在,且 再审申请书_姓名.pdf 存在
THEN  再审代理方向 = 被申请方
```

---

## 判断依据说明

- 起诉状、上诉状、再审申请书:律师自己起草时有 docx;法院/对方送达时只有 PDF
- 答辩状、代理词:无论代理哪一方律师均自己起草,docx 的存在**不能**作为判断依据
- 一审/二审/再审各自独立判断,首次触发时写入快照,长期保存,不重新判断

---

## 诉前保全阶段提前写入

一级目录出现 `财产保全申请书_姓名.docx` 时,提前写入快照 `representation_side_first = "原告"`,basis 标注"诉前保全阶段推断",后续发现有误可覆盖更新。

---

## 写入快照的字段

```json
{
  "first_instance":  { "representation_side": "原告",       "detected_at": "...", "basis": "1.起诉状和证据/起诉状_张三.docx 存在" },
  "second_instance": { "representation_side": "上诉人",     "detected_at": "...", "basis": "5.上诉状和证据/上诉状_张三.docx 存在" },
  "third_instance":  { "representation_side": "申请再审方", "detected_at": "...", "basis": "8.再审申请和证据/再审申请书_张三.docx 存在" }
}
```
