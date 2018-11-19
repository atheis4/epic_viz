CREATE DATABASE prov;
USE prov;

CREATE TABLE artifact
(
  artifact_id        INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  foreign_id         INT(11) UNSIGNED NOT NULL,
  PRIMARY KEY (artifact_id)
);

CREATE TABLE artifact_type
(
  artifact_type_id       INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  artifact_type_name     VARCHAR(255) NOT NULL,
  PRIMARY KEY (artifact_type_id)
);

ALTER TABLE artifact
ADD COLUMN artifact_type_id    INT(11) UNSIGNED NOT NULL,
ADD FOREIGN KEY (artifact_type_id) REFERENCES artifact_type(artifact_type_id);

CREATE TABLE tag
(
  tag_id            INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  tag_name          VARCHAR(255) NOT NULL,
  tag_name_short    VARCHAR(127) NOT NULL,
  PRIMARY KEY (tag_id)
);

CREATE TABLE tag_type
(
  tag_type_id      INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  tag_type_name    VARCHAR(255) NOT NULL,
  PRIMARY KEY (tag_type_id)
);

ALTER TABLE tag
ADD COLUMN tag_type_id    INT(11) UNSIGNED NOT NULL,
ADD FOREIGN KEY (tag_type_id) REFERENCES tag_type(tag_type_id);

CREATE TABLE artifact_tag
(
  artifact_id     INT(11) UNSIGNED NOT NULL,
  tag_id          INT(11) UNSIGNED NOT NULL,
  PRIMARY KEY (artifact_id, tag_id),
  FOREIGN KEY (artifact_id) REFERENCES artifact(artifact_id),
  FOREIGN KEY (tag_id) REFERENCES tag(tag_id)
);
