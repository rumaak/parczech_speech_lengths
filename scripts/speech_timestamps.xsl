<?xml version="1.0"?>

<!-- TODO there are a lot of for-eachs, maybe change to copy + match template? -->

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

                        <xsl:copy select=".">
                            <xsl:attribute name="who">
                                <xsl:value-of select="@who"/>
                            </xsl:attribute>

                            <xsl:for-each select="tei:seg">
                                <xsl:for-each select="tei:s">

                                    <xsl:for-each select="descendant::tei:anchor">
                                        <xsl:copy-of select="."/>
                                    </xsl:for-each>

                                </xsl:for-each>
                            </xsl:for-each>

                        </xsl:copy>
                    </xsl:for-each>
                </xsl:for-each>

                <xsl:copy-of select="tei:body/tei:timeline"/>

            </xsl:for-each>
        </root>
    </xsl:template>
</xsl:stylesheet> 
