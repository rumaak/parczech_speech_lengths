<?xml version="1.0"?>

<!--
    TODO description
-->


<xsl:stylesheet 
    version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fn="http://www.w3.org/2005/xpath-functions"
    xmlns:tei="http://www.tei-c.org/ns/1.0">
    <xsl:output method="text" omit-xml-declaration="yes" indent="no"/>

    <!-- Header row -->
    <xsl:template match="/">
        <xsl:text>id&#x9;</xsl:text>
        <xsl:text>type&#x9;</xsl:text>
        <xsl:text>name_cs&#x9;</xsl:text>
        <xsl:text>name_en&#x9;</xsl:text>
        <xsl:text>name_short&#x9;</xsl:text>
        <xsl:text>from&#x9;</xsl:text>
        <xsl:text>to&#x9;</xsl:text>
        <xsl:text>&#xA;</xsl:text>

        <xsl:apply-templates/>
    </xsl:template>

    <!-- Process affiliations with speaker in mind -->
    <xsl:template match="//tei:person">
        <xsl:apply-templates>
            <xsl:with-param name="id" select="@xml:id"/>
        </xsl:apply-templates>
    </xsl:template>
    
    <!-- Select only party or group affiliations -->
    <xsl:template match="tei:affiliation">
        <xsl:param name="id"/>

        <xsl:variable name="ref_hash" select="@ref"/>
        <xsl:variable name="ref" select="substring($ref_hash,2)"/>
        <xsl:variable name="type" select="substring-before($ref, '.')"/>

        <xsl:choose>
            <xsl:when test="($type = 'politicalParty') or  ($type = 'politicalGroup')">
                <xsl:call-template name="affiliation">
                    <xsl:with-param name="id" select="$id"/>
                    <xsl:with-param name="type" select="$type"/>
                    <xsl:with-param name="ref" select="$ref"/>
                </xsl:call-template>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <!-- Affiliation row -->
    <xsl:template name="affiliation">
        <xsl:param name="id"/>
        <xsl:param name="type"/>
        <xsl:param name="ref"/>

        <!-- id -->
        <xsl:value-of select="$id"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- type -->
        <xsl:value-of select="$type"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- name_cs, name_en, name_short -->
        <xsl:variable 
            name="org_path" 
            select="/tei:teiCorpus/tei:teiHeader/tei:profileDesc/tei:particDesc/tei:listOrg/tei:org"
        />
        <xsl:apply-templates select="$org_path[@xml:id=$ref]" mode="called"/>

        <!-- from -->
        <xsl:value-of select="@from"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- to -->
        <xsl:value-of select="@to"/>

        <xsl:text>&#xA;</xsl:text>
    </xsl:template>

    <!-- Affiliation name -->
    <xsl:template 
        match="/tei:teiCorpus/tei:teiHeader/tei:profileDesc/tei:particDesc/tei:listOrg/tei:org"
        mode="called"
    >
        <!-- name_cs -->
        <xsl:value-of select="tei:orgName[@xml:lang='cs']"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- name_en -->
        <xsl:value-of select="tei:orgName[@xml:lang='en']"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- name_short -->
        <xsl:value-of select="tei:orgName[@full='init']"/>
        <xsl:text>&#x9;</xsl:text>
    </xsl:template>

    <!-- Remove everything else -->
    <xsl:template match="text()" />

</xsl:stylesheet> 

