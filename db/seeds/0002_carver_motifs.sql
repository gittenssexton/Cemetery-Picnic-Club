-- Stonecarving visual vocabulary from the owner's Carvers_Section_Draft (2).pdf.
-- Research categories only: not maker identifications or evidence of presence at Pine Grove.
INSERT OR IGNORE INTO motifs(id,name,description) VALUES
('motif-winged-cherub','Winged cherub','Human-like central head accompanied by wings'),
('motif-deaths-head','Death’s-head','Skull-like funerary face; distinguish from a cherub'),
('motif-crowned-cherub','Crowned cherub','Winged face with crown or crown-like detail'),
('motif-portrait-head','Portrait face','Human face intended to resemble a portrait'),
('motif-hooded-face','Hooded oval face','Wingless oval head with raised hood-like outline'),
('motif-eyeglass-eyes','Eyeglass-like eyes','Close-spaced circular eyes connected to nose or mouth'),
('motif-pinwheel','Pinwheel','Radial geometric wheel or petal carving'),
('motif-rosette','Rosette','Floral or circular rosette ornament'),
('motif-volute','Volute','Large spiral side scroll'),
('motif-vine-border','Vine border','Vine or vine-leaf frame around inscription'),
('motif-ivy-border','Ivy-leaf border','Veined ivy-leaf decoration'),
('motif-diamond-border','Diamond border','Geometric diamond ornament'),
('motif-fleur-de-lis','Fleur-de-lis','Stylized lily or fleur-de-lis motif'),
('motif-hourglass','Hourglass','Time and mortality symbol'),
('motif-scythe-flower','Flower and scythe','Cut flower and scythe imagery'),
('motif-rooster','Rooster','Rooster/cockbird image'),
('motif-urn','Funerary urn','Neoclassical urn iconography'),
('motif-willow','Weeping willow','Willow tree or branches often paired with urn'),
('motif-feathered-wings','Detailed feathered wings','Wings with individually incised feathers');

INSERT OR IGNORE INTO craftspeople(id,display_name,alternate_names_json,biography_note,home_region,date_range_text) VALUES
('carver-jonathan-worcester','Jonathan Worcester','["Jonathan Worster"]','Working-draft style reference: mask-like linked facial features and pinwheels; individual attribution requires independent comparison','Harvard, Massachusetts','Active 1740s'),
('carver-daniel-hastings','Daniel Hastings','[]','Working-draft style reference: winged faces, vine borders, varying shop lettering and different slate phases','Newton, Massachusetts','Active by the 1780s'),
('carver-stebbins-workshop','Stebbins family / Longmeadow school','[]','Working-draft workshop reference: crowned cherubs, large scrolls, brown sandstone; distinguish Ezra I from successors','Longmeadow/Springfield, Massachusetts','1760s–early 1800s'),
('carver-sikes-workshop','Sikes family / imitators','[]','Working-draft school reference: hooded, wingless oval faces, schist/other stones and folk ornaments; imitators documented','Connecticut and western Massachusetts','1769–early 1800s'),
('carver-soule-family','Soule family / school','[]','Working-draft school reference: round staring eyes, detailed wings and later urn-and-willow forms; several named family members','Plympton to Worcester County, Massachusetts','1740s–1800s');

-- No maker-to-marker relationships are asserted by this vocabulary.
