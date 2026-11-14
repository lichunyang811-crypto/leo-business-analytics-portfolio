WITH history AS (SELECT * FROM records WHERE event_day <= '2026-10-31'),
consent AS (
 SELECT member_id, kind, ROW_NUMBER() OVER (
 PARTITION BY member_id ORDER BY event_day DESC, (kind='opt_out') DESC, event_id DESC
 ) AS rn FROM history WHERE kind <> 'send'
), activity AS (
 SELECT member_id, MAX(CASE WHEN kind='send' THEN event_day END) AS last_send FROM history GROUP BY member_id
)
SELECT a.member_id, c.kind AS latest_consent, a.last_send,
 CASE WHEN c.kind IS NULL THEN 'no_consent' WHEN c.kind='opt_out' THEN 'opted_out'
 WHEN a.last_send > date('2026-10-31','-7 days') THEN 'cooldown' ELSE 'eligible' END AS decision
FROM activity a LEFT JOIN consent c ON c.member_id=a.member_id AND c.rn=1 ORDER BY a.member_id
