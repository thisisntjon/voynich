import runpy, sys, os
g = runpy.run_path(sys.argv[1]); R = sys.argv[2]; J = lambda *a: os.path.join(R, *a)
specs = [('APICIUS', lambda: g['gut_lines'](J('r11','dl_PG16439','pg16439.txt'))),
 ('DIGBY', lambda: g['gut_lines'](J('r11','dl_PG16441','pg16441.txt'), lambda l: l.startswith('A RECEIPT TO MAKE METHEGLIN AS IT IS MADE AT LIEGE'))),
 ('ROGET', lambda: g['gut_lines'](J('r11','dl_PG10681','pg10681.txt'), lambda l: l.startswith('1. Existence'))),
 ('CULPEPER', lambda: g['gut_lines'](J('r11','dl_PG49513','pg49513.txt'), lambda l: l.strip()=='AMARA DULCIS.')),
 ('KALEVALA', lambda: g['gut_lines'](J('r11','dl_PG7000','pg7000.txt'), lambda l: l.strip()=='Ensimmäinen runo')),
 ('BALLADS', lambda: g['gut_lines'](J('r11','dl_PG44969','pg44969.txt'), lambda l: l.strip()=='RIDDLES WISELY EXPOUNDED', nth=1)),
 ('LITANIES', lambda: g['gut_lines'](J('r11','dl_PG62988','pg62988.txt'), lambda l: l.strip()=='Litany Of The Holy Name Of Jesus.')),
 ('PRAYERS', lambda: g['gut_lines'](J('r11','dl_PG48242','pg48242.txt'))),
 ('CREMMA', lambda: g['cremma_lines'](R)),
 ('HEBREW', lambda: g['hebrew_lines']([J('r11','dl_WLC','Gen.xml'), J('r11','dl_WLC','Exod.xml')])),
 ('DANTE', lambda: g['dante_lines'](J('dl_DANTE','pg1000.txt')))]
for n, f in specs:
    L = f(); b = g['blocks'](L)
    print(n, 'lines', len(L), 'words', sum(map(len, L)), '-> used words', sum(len(x[2]) for x in b), 'sample:', ' '.join(L[0][:6]).encode('ascii','backslashreplace').decode()[:70])
