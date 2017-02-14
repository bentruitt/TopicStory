lines = []
lines.append('CREATE TABLE IF NOT EXISTS article_headline_vector (\n')
lines.append('   url INTEGER REFERENCES urls(id) PRIMARY KEY,\n')
for i in range(299):
    lines.append('    X_{} FLOAT NOT NULL,\n'.format(i))
lines.append('    X_299 FLOAT NOT NULL\n')
lines.append(')\n')

with open('schema-nlp.sql', 'w') as f:
    f.writelines(lines)
