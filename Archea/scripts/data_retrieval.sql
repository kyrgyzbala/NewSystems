select s1.*, s2.*
from (
		select ap.id ,count(*) as cnt, sum(w.weight) as wgt
		from archea_5plets ap
		inner join archea_5plets_win10 apw on ap.id = apw.kplet_id
		inner join archea_win10_files awf on apw.file_id = awf.id
		inner join sources s on awf.source_id=s.id
		inner join weights w on w.genome_id=s.genome_id
		group by ap.id ) s1
inner join tmp s2 on s1.id=s2.id
order by s1.wgt;


select ap.id ,count(*) as cnt, sum(w.weight) as wgt
from archea_5plets ap
inner join archea_5plets_win10 apw on ap.id = apw.kplet_id
inner join archea_win10_files awf on apw.file_id = awf.id
inner join sources s on awf.source_id=s.id
inner join weights w on w.genome_id=s.genome_id
group by ap.id;