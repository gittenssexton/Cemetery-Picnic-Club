-- Reference features sourced from NPS cemetery preservation and AGS preservation guidance.
-- Material descriptions are diagnostic clues, never a definitive automatic determination.
INSERT OR IGNORE INTO material_types
(id,display_name,geology_class,distinguishing_features,known_ambiguities) VALUES
('material-slate','Slate','metamorphic','Fine-grained; usually smooth and dark gray, blue, or black; planar cleavage; detailed shallow incisions may survive well.','Fine-grained schist and phyllite may appear similar; dark surface staining is not diagnostic.'),
('material-sandstone','Sandstone / brownstone','sedimentary','Visible sand-size grains; brown/red/gray hues; bedding and granular weathering.','Color can vary; coatings can conceal grains; some stones are sold under commercial names.'),
('material-marble','Marble','metamorphic','Recrystallized carbonate; may show crystalline or sugary weathering, veining and pale colors.','Limestone and commercial marble labels can overlap; photography alone cannot verify carbonate chemistry.'),
('material-limestone','Limestone','sedimentary','Fine to granular carbonate rock; sometimes fossils; often tan, buff or gray.','May resemble marble; fossils may be absent; do not perform acid tests on monuments.'),
('material-granite','Granite','igneous','Visible interlocking quartz and feldspar crystals; generally speckled; frequently polished.','Commercial granite may include gneiss and other hard stones; polished surfaces obscure texture.'),
('material-schist','Schist','metamorphic','Often micaceous and foliated with visible layered or flaky mineral alignment.','Fine schist, phyllite and slate may be difficult to separate without close geological examination.'),
('material-gneiss','Gneiss','metamorphic','Banded mineral assemblages, commonly alternating light and dark layers.','Commercial stone terminology may call gneiss granite.'),
('material-soapstone','Soapstone','metamorphic','Talc-rich, generally fine-grained gray, greenish or mottled rock.','Color and surface feel alone are weak evidence; no scratching or other tests on historic stone.'),
('material-zinc','Zinc / white bronze','metal','Cast metal monuments can show hollow construction, panels and sharply repeating cast ornament.','Not natural stone; corrosion or surface finish may mimic masonry.'),
('material-concrete','Concrete / cast stone','manufactured','Cementitious material with visible aggregate or casting features.','May be finished or colored to simulate natural stone.');

INSERT OR IGNORE INTO research_works
(id,title,authors,work_type,url,full_text_status,rights_status,review_status) VALUES
('work-nps-materials','Materials and Monuments','National Park Service','government','https://www.nps.gov/articles/000/cemetery-preservation-course-materials-and-monuments.htm','available_external','check_publication_rights','partly_reviewed'),
('work-ags-identifying-stone','Identifying Major Stone Types','Association for Gravestone Studies','web','https://www.gravestonestudies.org/component/content/article/88-preservationconservation/100-preservation-and-conservation-2','available_external','check_publication_rights','partly_reviewed'),
('work-mass-historic-markers','Preservation Guidelines for Municipally Owned Historic Burial Grounds and Cemeteries','Commonwealth of Massachusetts','government','https://www.mass.gov/doc/preservation-guidelines-for-municipally-owned-historic-burial-grounds-and-cemeteries/download','available_external','check_publication_rights','partly_reviewed');

INSERT OR IGNORE INTO material_reference_sources(material_id,work_id,locator,evidence_note) VALUES
('material-slate','work-nps-materials','Masonry','NPS identifies slate as silicate metamorphic stone'),
('material-slate','work-ags-identifying-stone','Slate','Visible fine grain, cleavage and common colors'),
('material-sandstone','work-ags-identifying-stone','Sandstone','Visible sand grains and bedding'),
('material-marble','work-ags-identifying-stone','Marble','Crystalline weathering, veins and visual ambiguity'),
('material-limestone','work-ags-identifying-stone','Limestone','Carbonate character and possible fossils'),
('material-granite','work-ags-identifying-stone','Granite','Interlocking visible grains and commercial misnaming'),
('material-schist','work-nps-materials','Masonry','Metamorphic schist cited as silicate stone'),
('material-soapstone','work-ags-identifying-stone','Soapstone','Talc-rich metamorphic stone description'),
('material-zinc','work-mass-historic-markers','Grave Markers','Late nineteenth-century white bronze/zinc markers'),
('material-concrete','work-nps-materials','Masonry','Manufactured cement-based masonry material');

-- No real marker receives an inferred stone type from these reference entries.
