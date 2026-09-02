c = open('/home/madfella/peptidetrack/templates/index.html').read()
old = '''      #report-overlay .no-print { display: none !important; }
    }
  </style>
</head>'''
new = '''      #report-overlay .no-print { display: none !important; }
    }
  </style>
  <script async src="https://cdn.mosa.click/v1/mosa.js" data-site-id="3daea132-0f5e-430b-a435-620a06bac048" data-eu="true"></script>
</head>'''
print("count:", c.count(old))
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/templates/index.html', 'w').write(c)
print("written")
