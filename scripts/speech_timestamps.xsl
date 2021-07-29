<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0">
    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
    <xsl:template match="/">
        <root>
            <!--
                We assume that <text> elements contain the speeches and only
                the speeches we care about. This should make sense given the
                Parla-CLARIN schema.
            -->
            <xsl:for-each select="//tei:text">
                <!--
                    Each <text> has to contain <body>, which holds the data
                    we care about. There might be potentially multiple divs.
                -->
                <xsl:for-each select="tei:body/tei:div">
                    <xsl:for-each select="tei:u">
                        <--! TODO select only relevant data -->
                        <xsl:value-of select="."/>
                    </xsl:for-each>
                </xsl:for-each>
            </xsl:for-each>
        </root>
    </xsl:template>
</xsl:stylesheet> 
