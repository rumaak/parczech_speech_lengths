<?xml version="1.0"?>

<!--
    This script extracts data about all people specified in the input XML
    file.
    
    The resulting file consists of header row followed by a single row
    for each person. Columns are tab-separated.
-->

<xsl:stylesheet 
    version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fn="http://www.w3.org/2005/xpath-functions"
    xmlns:tei="http://www.tei-c.org/ns/1.0">
    <xsl:output method="text" omit-xml-declaration="yes" indent="no"/>

    <!-- Header row -->
    <xsl:template match="/">
        <!-- TODO affliations -->

        <xsl:text>id&#x9;</xsl:text>
        <xsl:text>surname&#x9;</xsl:text>
        <xsl:text>forename&#x9;</xsl:text>
        <xsl:text>sex&#x9;</xsl:text>
        <xsl:text>birth&#x9;</xsl:text>
        <xsl:text>picture&#x9;</xsl:text>
        <xsl:text>&#xA;</xsl:text>

        <xsl:apply-templates/>
    </xsl:template>

    <!-- Person row -->
    <xsl:template match="//tei:person">
        <!-- id -->
        <xsl:value-of select="@xml:id"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- surname -->
        <xsl:value-of select="tei:persName/tei:surname"/>
        <xsl:text>&#x9;</xsl:text>
        
        <!-- forename -->
        <xsl:value-of select="tei:persName/tei:forename"/>
        <xsl:text>&#x9;</xsl:text>
        
        <!-- sex -->
        <xsl:value-of select="tei:sex/@value"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- birth -->
        <xsl:value-of select="tei:birth/@when"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- picture -->
        <xsl:value-of select="tei:figure/tei:graphic/@url"/>

        <xsl:text>&#xA;</xsl:text>
    </xsl:template>

    <!-- Remove everything else -->
    <xsl:template match="text()" />

</xsl:stylesheet> 

